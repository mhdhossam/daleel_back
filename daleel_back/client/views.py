from django.shortcuts import render
from rest_framework import status,viewsets,generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CustomUser
from .serializers import UserRegistrationSerializer

class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import status
from .models import Vendor, Customer

class LoginView(APIView):
    """
    Login view to authenticate users and generate JWT tokens.
    Supports both Vendor and Customer models.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Identify user type
        if isinstance(user, Vendor):
            user_type = "Vendor"
            additional_data = {
                "business_name": user.business_name,
                "business_address": user.business_address
            }
        elif isinstance(user, Customer):
            user_type = "Customer"
            additional_data = {
                "shipping_address": user.shipping_address
            }
        else:
            user_type = "User"
            additional_data = {}

        # Generate JWT Tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Response
        return Response({
            'message': f"Login successful as {user_type}.",
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'user_type': user_type,
                **additional_data
            },
            'jwt_tokens': {
                'access': access_token,
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)
