from django.urls import path

from .views import TransactionListView,  AirtimePurchaseView

urlpatterns = [
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('airtime/purchase/', AirtimePurchaseView.as_view()),
]