from django.urls import path
from .views import InitiateFundingView

urlpatterns = [
    path("initiate/", InitiateFundingView.as_view()),
]