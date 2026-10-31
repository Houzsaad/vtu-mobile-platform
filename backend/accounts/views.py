from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import LoginSerializer

from .serializers import ChangePasswordSerializer
from .serializers import ChangePinSerializer


from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import status

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from .serializers import ForgotPasswordRequestSerializer
from .serializers import ForgotPasswordConfirmSerializer

from .models import OTPCode

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "Registration successful.", "username": user.username},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class ProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)


class ChangePinView(generics.GenericAPIView):
    serializer_class = ChangePinSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Transaction PIN changed successfully."}, status=status.HTTP_200_OK)




class ForgotPasswordRequestView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        s = ForgotPasswordRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        email = s.validated_data["email"]

        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            code = OTPCode.issue(user, OTPCode.Purpose.PASSWORD_RESET)
            try:
                send_mail(
                    subject=f"{settings.APP_NAME} password reset code",
                    message=(f"Your password reset code is {code}.\n"
                             "It expires in 10 minutes. If you didn't ask for it, ignore this email."),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )
            except Exception:
                pass  # never reveal failures or whether the account exists

        return Response({"message": "If that email is registered, a reset code has been sent."})





class ForgotPasswordConfirmView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        s = ForgotPasswordConfirmSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        user = User.objects.filter(email__iexact=d["email"], is_active=True).first()

        with transaction.atomic():
            if not (user and OTPCode.verify(user, OTPCode.Purpose.PASSWORD_RESET, d["code"])):
                # returning normally commits the failed-attempt count
                return Response({"detail": "Invalid or expired code."},
                                status=status.HTTP_400_BAD_REQUEST)

            if user.check_password(d["new_password"]):
                transaction.set_rollback(True)  # keeps the code usable
                return Response(
                    {"new_password": ["New password cannot be the same as your current password."]},
                    status=status.HTTP_400_BAD_REQUEST)

            user.set_password(d["new_password"])
            user.save(update_fields=["password"])

        return Response({"message": "Password reset successful. You can now log in."})

# Create your views here.





