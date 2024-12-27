from django.shortcuts import render
from django.conf import settings
from rest_framework import status,viewsets,generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CustomUser,Vendor, Customer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer,VendorRegisterSerializer, CustomerRegisterSerializer


# Vendor Registration View
class VendorRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = VendorRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Vendor registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Customer Registration View
class CustomerRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomerRegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Customer registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom Login View to issue JWT tokens with extended payload.
    """
    serializer_class = CustomTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data

        access_token = data.get('access')
        refresh_token = data.get('refresh')

        # Set cookies for tokens
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=settings.DEBUG is True,
            samesite='Lax',
            max_age=60 * 15,  # 15 minutes
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=settings.DEBUG is True,
            samesite='Lax',
            max_age=60 * 60 * 24,  # 1 day
        )

        # Remove tokens from response body
        # del response.data['refresh']
        # del response.data['access']
        return response



class LogoutView(APIView):
    """
    Logout view to blacklist refresh token and clear cookies.
    """
    permission_classes=[IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            response = Response({"message": "Logged out successfully"}, status=200)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    

