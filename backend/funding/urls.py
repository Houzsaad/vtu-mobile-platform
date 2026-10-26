from django.urls import path
from .views import InitiateFundingView, PaystackWebhookView, FundingStatusView

urlpatterns = [
    path("initiate/", InitiateFundingView.as_view()),
    path("webhook/", PaystackWebhookView.as_view()),
    path("<str:reference>/", FundingStatusView.as_view()),
]