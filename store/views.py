from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
    DestroyAPIView,
    
)
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from.models import * 
from.serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from client.permissions import IsVendorPermission
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError,PermissionDenied
from decimal import Decimal
import requests
from django.core.files.base import ContentFile
import os
from PIL import Image
from io import BytesIO


class CategoryListView(APIView):
    """
    API view to retrieve all categories as choices.
    """
    def get(self, request):
        categories = Category.objects.all()
        serialized_categories = CategorySerializer(categories, many=True).data
        # Format categories as choices
        choices = [{'value': category['id'], 'label': category['name']} for category in serialized_categories]
        return Response(choices)
    
class ProductListView(ListAPIView):
    """
    API view to retrieve a list of all products with filters, search, and pagination.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['id','category']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'sold_count', 'title']

class VendorDashboardView(APIView):
    """
    Dashboard for vendors to manage their products.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVendorPermission]

    def get(self, request):
        """
        List all products owned by the vendor.
        """
        vendor = request.user.vendor
        products = Product.objects.filter(vendor=vendor)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new product for the vendor.
        """
        vendor = request.user.vendor
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(vendor=vendor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    



import logging

logger = logging.getLogger(__name__)

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import requests
import os
from .models import Product
from .serializers import ProductCreateSerializer
from client.permissions import IsVendorPermission
import logging

logger = logging.getLogger(__name__)

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.files.base import ContentFile
import requests
import os
from .models import Product
from .serializers import ProductCreateSerializer
from client.permissions import IsVendorPermission


class ProductUpdateView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVendorPermission]
    serializer_class = ProductCreateSerializer

    def get_queryset(self):
        """
        Override get_queryset to handle image processing for products with URL-based images.
        Downloads the image if the `image` field is a URL.
        """
        queryset = Product.objects.all()

        for product in queryset:
            # If the image is a URL, fetch and save it as a file
            if isinstance(product.image, str) and product.image.startswith(("http://", "https://")):
                try:
                    response = requests.get(product.image, stream=True)
                    response.raise_for_status()

                    # Extract filename from the URL
                    file_name = os.path.basename(product.image.split("?")[0])

                    # Save the image to the media directory
                    content_file = ContentFile(response.content, name=file_name)
                    product.image.save(file_name, content_file, save=True)
                except requests.RequestException as e:
                    print(f"Failed to fetch image for product {product.id}: {e}")

        return queryset

    def update(self, request, *args, **kwargs):
        """
        Handle the update request for the product.
        """
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        # Handle the image field if provided as part of the update
        image = validated_data.get("image")
        if image:
            if isinstance(image, str):  # If image is a URL
                try:
                    response = requests.get(image, stream=True)
                    response.raise_for_status()

                    # Extract filename from the URL
                    file_name = os.path.basename(image.split("?")[0])

                    # Save the image to the media directory
                    content_file = ContentFile(response.content, name=file_name)
                    product.image.save(file_name, content_file, save=True)
                except requests.RequestException as e:
                    return Response({"image_error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:  # Handle file uploads
                product.image = image

        # Update other fields
        for attr, value in validated_data.items():
            if attr != "image":
                setattr(product, attr, value)

        product.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

        

       


    
class ProductDeleteView(generics.DestroyAPIView):
    """
    API view to allow only vendors to delete their products.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVendorPermission]
    queryset = Product.objects.all()

    def get_queryset(self):
        """
        Ensure that vendors can only delete their own products.
        """
        user = self.request.user
        if hasattr(user, 'vendor'):  # Check if user is a vendor
            return Product.objects.filter(vendor=user.vendor)
        return Product.objects.none()

class ProductDetailView(RetrieveAPIView):
    """
    API view to retrieve a single product by its ID using RetrieveAPIView.
    """
    serializer_class = ProductDetailSerializer

    def get_object(self):
        """
        Retrieve the product instance by its ID.
        """
        product_id = self.kwargs.get("id")  # Get the 'id' from the URL
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        """
        Handle the GET request for product details.
        """
        product = self.get_object()
        if not product:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(product)
        return Response(serializer.data)

class ProductCreateView(CreateAPIView):
    """
    API view to allow only vendors to create products.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVendorPermission]
    serializer_class = ProductCreateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user) 


class AddToCartView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve or create cart
        cart, created = Order.objects.get_or_create(user=user, status='CART')

        # Retrieve or create order item
        order_item, created = OrderItem.objects.get_or_create(
            order=cart, product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )

        if not created:
            order_item.quantity += int(quantity)
            order_item.save()

        cart.calculate_total_price()

        return Response(OrderSerializer(cart).data, status=status.HTTP_200_OK)

class RemoveFromCartView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        user = request.user
        try:
            cart = Order.objects.get(user=user, status='CART')
            order_item = cart.order_items.get(pk=pk)
        except (Order.DoesNotExist, OrderItem.DoesNotExist):
            return Response({"error": "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND)

        order_item.delete()
        cart.calculate_total_price()

        return Response({"message": "Item removed from cart."}, status=status.HTTP_200_OK)

class UpdateCartView(UpdateAPIView):
    """
    Update the quantity of a product in the cart using the PATCH method.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        """
        Return the queryset for the items in the user's cart.
        Raise an error if no cart or item is found.
        """
        user = self.request.user
        cart = Order.get_cart(user)
        if not cart:
            raise serializers.ValidationError("No active cart found.")
        return OrderItem.objects.filter(order=cart)

    def partial_update(self, request, *args, **kwargs):
        """
        Handle partial updates for OrderItem.
        """
        instance = self.get_object()
        quantity = int(request.data.get('quantity', 1))

        if quantity <= 0:
            instance.delete()
        else:
            instance.quantity = quantity
            instance.save()

        # Recalculate cart total price
        cart = instance.order
        cart.calculate_total_price()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class ViewCartView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cart = Order.objects.filter(user=user, status='CART').first()
        if not cart:
            return Response({"error": "Cart is empty."}, status=status.HTTP_404_NOT_FOUND)

        return Response(OrderSerializer(cart).data, status=status.HTTP_200_OK)

class WishlistView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = Customer.objects.get(id=request.user.id)
        wishlist_items = Favorite.objects.filter(customer=customer)
        products = [favorite.product for favorite in wishlist_items]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=200)
    
class AddToWishlistView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=404)

        try:
            # Fetch the corresponding Customer instance
            customer = Customer.objects.get(id=request.user.id)
        except Customer.DoesNotExist:
            return Response({"error": "Customer profile not found."}, status=404)

        # Create or get the favorite entry
        favorite, created = Favorite.objects.get_or_create(customer=customer, product=product)

        if not created:
            return Response({"message": "Product is already in your wishlist."}, status=200)

        return Response({"message": "Product added to wishlist."}, status=201)

class RemoveFromWishlistView(DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        try:
            favorite = Favorite.objects.get(customer=request.user, product_id=product_id)
            favorite.delete()
            return Response({"message": "Product removed from wishlist."}, status=200)
        except Favorite.DoesNotExist:
            return Response({"error": "Product not in your wishlist."}, status=404)
