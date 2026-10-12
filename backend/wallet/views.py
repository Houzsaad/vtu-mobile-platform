from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionPagination(PageNumberPagination):
    page_size = 20


class TransactionListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user)
    
# Create your views here.
