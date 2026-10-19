from django.urls import path

from .views import TransactionListView,  AirtimePurchaseView, DataPlanListView, DataPurchaseView

urlpatterns = [
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('airtime/purchase/', AirtimePurchaseView.as_view()),

    path('data/plans/', DataPlanListView.as_view()),
    path('data/purchase/', DataPurchaseView.as_view()),
]