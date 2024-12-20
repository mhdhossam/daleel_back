from rest_framework import serializers
from .models import Vendor, Customer,CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# Base Registration Serializer
class BaseUserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, required=True)


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

        # Explicitly check for related Vendor or Customer model
        try:
            if hasattr(user, 'vendor'):
                vendor = Vendor.objects.get(pk=user.pk)  # Load vendor data
                token['user_type'] = 'Vendor'
                token['business_name'] = vendor.business_name
                token['business_address'] = vendor.business_address
            elif hasattr(user, 'customer'):
                customer = Customer.objects.get(pk=user.pk)  # Load customer data
                token['user_type'] = 'Customer'
                token['shipping_address'] = customer.shipping_address
            else:
                token['user_type'] = 'User'
        except (Vendor.DoesNotExist, Customer.DoesNotExist):
            token['user_type'] = 'User'

        return token

