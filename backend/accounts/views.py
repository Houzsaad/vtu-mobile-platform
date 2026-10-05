from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, LoginSerializer


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


from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import LoginSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

# Create your views here.
