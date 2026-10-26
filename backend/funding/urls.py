from django.urls import path
from .views import InitiateFundingView, PaystackWebhookView

urlpatterns = [
    path("initiate/", InitiateFundingView.as_view()),
    path("webhook/", PaystackWebhookView.as_view()),
]