from django.urls import path
from .views import RegisterView, LoginView, ProfileView, ChangePasswordView, ChangePinView, ForgotPasswordRequestView, ForgotPasswordConfirmView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('change-pin/', ChangePinView.as_view(), name='change-pin'),

    path("forgot-password/", ForgotPasswordRequestView.as_view()),
    path("forgot-password/confirm/", ForgotPasswordConfirmView.as_view()),
]