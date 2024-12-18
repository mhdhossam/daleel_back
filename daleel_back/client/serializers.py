from rest_framework import serializers
from .models import Vendor, Customer,CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# Base Registration Serializer
class BaseUserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


# Vendor Registration Serializer
class VendorRegisterSerializer(BaseUserRegisterSerializer):
    business_name = serializers.CharField(max_length=255, required=True)
    business_address = serializers.CharField(required=True)

    class Meta(BaseUserRegisterSerializer.Meta):
        model = Vendor
        fields = BaseUserRegisterSerializer.Meta.fields + ['business_name', 'business_address']

    def create(self, validated_data):
        business_name = validated_data.pop('business_name')
        business_address = validated_data.pop('business_address')
        user = Vendor.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            business_name=business_name,
            business_address=business_address
        )
        return user


# Customer Registration Serializer
class CustomerRegisterSerializer(BaseUserRegisterSerializer):
    shipping_address = serializers.CharField(required=True)

    class Meta(BaseUserRegisterSerializer.Meta):
        model = Customer
        fields = BaseUserRegisterSerializer.Meta.fields + ['shipping_address']

    def create(self, validated_data):
        shipping_address = validated_data.pop('shipping_address')
        user = Customer.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            shipping_address=shipping_address
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        """
        Customize the JWT payload to include user-specific data.
        """
        token = super().get_token(user)

        # Add default claims
        token['username'] = user.username
        token['email'] = user.email

        # Determine user type and add specific fields
        if hasattr(user, 'business_name'):
            token['user_type'] = 'Vendor'
            token['business_name'] = user.business_name
            token['business_address'] = user.business_address
        elif hasattr(user, 'shipping_address'):
            token['user_type'] = 'Customer'
            token['shipping_address'] = user.shipping_address
        else:
            token['user_type'] = 'User'

        return token
