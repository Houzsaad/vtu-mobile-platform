from django.urls import path
from .views import RegisterView, LoginView, ProfileView, ChangePasswordView, ChangePinView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('change-pin/', ChangePinView.as_view(), name='change-pin'),
]