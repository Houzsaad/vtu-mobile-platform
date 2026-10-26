import uuid

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FundingRequest
from .paystack import clamp_expiry, create_transfer_charge
from .serializers import FundingRequestSerializer, InitiateFundingSerializer


class InitiateFundingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = InitiateFundingSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        amount = s.validated_data["amount"]

        # Reuse the live request for the same amount instead of calling Paystack again
        existing = FundingRequest.objects.filter(
            user=request.user, amount=amount,
            status=FundingRequest.Status.PENDING,
            expires_at__gt=timezone.now(),
        ).first()
        if existing:
            return Response(FundingRequestSerializer(existing).data)

        funding = FundingRequest.objects.create(
            user=request.user, amount=amount, reference=uuid.uuid4().hex)

        ok, data = create_transfer_charge(
            email=request.user.email,
            amount_naira=amount,
            reference=funding.reference,
            expires_at=clamp_expiry(),
        )
        info = data.get("data") or {}
        if not ok or not info.get("account_number"):
            funding.status = FundingRequest.Status.EXPIRED
            funding.raw = data
            funding.save(update_fields=["status", "raw", "updated_at"])
            return Response(
                {"detail": "Could not create a funding account. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY)

        funding.bank_name = (info.get("bank") or {}).get("name", "")
        funding.account_number = info["account_number"]
        funding.account_name = info.get("account_name", "")
        funding.expires_at = parse_datetime(info.get("account_expires_at") or "")
        funding.raw = data
        funding.save()

        return Response(FundingRequestSerializer(funding).data, status=status.HTTP_201_CREATED)

# Create your views here.
