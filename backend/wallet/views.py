from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import Transaction, DataPlan
from .serializers import TransactionSerializer, DataPlanSerializer, DataPurchaseSerializer
from .services import purchase_data, PlanUnavailable


from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import AirtimePurchaseSerializer
from .services import (
    purchase_airtime, verify_transaction_pin,
    InvalidPin, InsufficientFunds, DuplicateReferenceMismatch,
)

from django.conf import settings


class TransactionPagination(PageNumberPagination):
    page_size = 20


class TransactionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user)



class AirtimePurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = AirtimePurchaseSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        try:
            verify_transaction_pin(request.user, d['pin'])
        except InvalidPin:
            return Response({'detail': 'Invalid transaction PIN.'}, status=403)

        try:
            txn = purchase_airtime(
                wallet_id=request.user.wallet.id,
                network=d['network'],
                phone=d['phone'],
                amount=d['amount'],
            )
        except InsufficientFunds:
            return Response({'detail': 'Insufficient wallet balance.'}, status=400)
        except DuplicateReferenceMismatch:
            return Response({'detail': 'Duplicate request.'}, status=409)

        return Response({
            'status': txn.status,
            'amount': txn.amount,
            'recipient': txn.recipient,
            'network': txn.network,
            'reference': txn.reference,
        }, status=200)


class DataPlanListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plans = DataPlan.objects.filter(is_active=True, provider=settings.VTU_PROVIDER)
        network = request.query_params.get('network')
        if network:
            plans = plans.filter(network=network)
        return Response(DataPlanSerializer(plans, many=True).data)


class DataPurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        s = DataPurchaseSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        try:
            verify_transaction_pin(request.user, d['pin'])
        except InvalidPin:
            return Response({'detail': 'Invalid transaction PIN.'}, status=403)

        try:
            txn = purchase_data(
                wallet_id=request.user.wallet.id,
                plan_id=d['plan_id'],
                phone=d['phone'],
            )
        except PlanUnavailable:
            return Response({'detail': 'This plan is unavailable.'}, status=400)
        except InsufficientFunds:
            return Response({'detail': 'Insufficient wallet balance.'}, status=400)
        except DuplicateReferenceMismatch:
            return Response({'detail': 'Duplicate request.'}, status=409)

        return Response({
            'status': txn.status,
            'amount': txn.amount,
            'recipient': txn.recipient,
            'network': txn.network,
            'plan': txn.description,
            'reference': txn.reference,
        }, status=200)
    
# Create your views here.
