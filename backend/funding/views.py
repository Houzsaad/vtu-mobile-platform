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

import hashlib
import hmac
import json
from decimal import Decimal

from django.conf import settings
from django.db import transaction as db_transaction
from rest_framework.permissions import AllowAny

from wallet.services import credit_wallet


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

### WEEBHOOK ARENA ###

def _valid_signature(raw_body, signature):
    expected = hmac.new(settings.PAYSTACK_SECRET_KEY.encode(),
                        raw_body, hashlib.sha512).hexdigest()
    return hmac.compare_digest(expected, signature or "")


class PaystackWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        raw = request.body  # read before touching request.data
        if not _valid_signature(raw, request.headers.get("x-paystack-signature")):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            event = json.loads(raw)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = event.get("data") or {}
        if event.get("event") != "charge.success" or data.get("channel") != "bank_transfer":
            return Response(status=status.HTTP_200_OK)  # not ours, ignore

        with db_transaction.atomic():
            funding = (FundingRequest.objects.select_for_update()
                       .filter(reference=data.get("reference")).first())
            if funding is None or funding.status == FundingRequest.Status.SUCCESS:
                return Response(status=status.HTTP_200_OK)

            received = Decimal(str(data.get("amount", 0))) / 100
            funding.raw = event
            funding.amount_received = received

            exact = (received == funding.amount and data.get("currency", "NGN") == "NGN")
            on_time = funding.status == FundingRequest.Status.PENDING

            if exact and on_time:
                credit_wallet(
                    wallet_id=funding.user.wallet.id,
                    amount=funding.amount,
                    provider="paystack",
                    reference=funding.reference,
                )
                funding.status = FundingRequest.Status.SUCCESS
            else:
                funding.status = FundingRequest.Status.REVIEW  # money arrived, a human decides

            funding.save()

        return Response(status=status.HTTP_200_OK)
# Create your views here.
