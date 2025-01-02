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



class ProductUpdateView(generics.UpdateAPIView):
    """
    API view to allow only vendors to update their products.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVendorPermission]
    serializer_class = ProductCreateSerializer

    def get_queryset(self):
        """
        Ensure that vendors can only update their own products.
        """
        user = self.request.user
        if hasattr(user, 'vendor') and user.vendor.is_vendor:
            return Product.objects.filter(vendor=user.vendor)
        return Product.objects.none()

    def update(self, request, *args, **kwargs):
        """
        Handle the update request and provide meaningful responses.
        """
        product = self.get_object()
        if not product:
            return Response(
                {"error": "Product not found or unauthorized access."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if product.vendor != request.user.vendor:
            raise PermissionDenied("You do not have permission to edit this product.")

        partial = kwargs.pop("partial", False)  # Allow partial updates
        serializer = self.get_serializer(product, data=request.data, partial=partial)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            print(f"Validation Errors: {e.detail}")  # Log validation errors
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)

        return Response(
            {"message": "Product updated successfully!", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def perform_update(self, serializer):
        """
        Save the updated product data and handle optional image updates.
        """
        instance = serializer.instance
        validated_data = serializer.validated_data

        # Update image only if provided
        if "image" in validated_data:
            instance.image = validated_data["image"]

        # Update other fields dynamically
        for attr, value in validated_data.items():
            if attr != "image":  # Skip image, as it's already handled
                setattr(instance, attr, value)

        instance.save()
    
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
        """
        Override the perform_create method to include vendor assignment.
        """
        # Ensure the user is associated with a vendor
        try:
            vendor = self.request.user.vendor  # Assuming the `Vendor` model has a OneToOneField to `User`
        except Vendor.DoesNotExist:
            raise PermissionDenied("You must be a vendor to create products.")

        # Save the product with the associated vendor
        serializer.save(vendor=vendor)

#jgkjg
class AddToCartView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user.customer
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
        
from rest_framework.exceptions import ValidationError

class CheckoutView(APIView):
    """
    View to handle the checkout process.
    Automatically fetches user_id and order_id based on the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        serializer = CheckoutSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Get the authenticated user
            user = request.user
            if not hasattr(user, 'customer'):
                return Response({"error": "User is not a customer."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the user's cart (Order with status 'CART')
            try:
                cart = Order.objects.get(user=user.customer, status='CART')
            except Order.DoesNotExist:
                return Response({"error": "Cart not found or is empty."}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate total price
            cart.calculate_total_price()

            # Process payment
            payment_method = serializer.validated_data['payment_method']
            shipping_address = serializer.validated_data['shipping_address']

            if payment_method == 'INSTAPAY':
                payment_status = True  # Simulate successful payment
            elif payment_method == 'CASH':
                payment_status = True  # Cash on delivery
            else:
                return Response({"error": "Invalid payment method."}, status=status.HTTP_400_BAD_REQUEST)

            # Save Checkout entry
            checkout = Checkout.objects.create(
                user=user.customer,
                order=cart,
                payment_method=payment_method,
                shipping_address=shipping_address,
                payment_status='PAID' if payment_status else 'FAILED'
            )
            print(checkout)

            # Update cart status to 'PAID'
            cart.status = 'PAID'
            cart.save()

            return Response({
                "message": "Checkout successful.",
                "checkout_id": checkout.id,
                "total_price": cart.total_price,
                "status": cart.status,
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckoutRetrieveAPIView(RetrieveAPIView):
    """
    API view to retrieve the checkout details for a user's order.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    def get_object(self):
        """
        Retrieve the checkout object for the user's pending order.
        """
        try:
            order = Order.objects.get(user=self.request.user, status='PENDING')
            checkout = Checkout.objects.get(order=order)
            return checkout
        except Order.DoesNotExist:
            raise ValidationError("No pending order found.")
        except Checkout.DoesNotExist:
            raise ValidationError("Checkout details not found.")
        
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and returns the checkout details.
        """
        checkout = self.get_object()
        serializer = self.get_serializer(checkout)
        return Response(serializer.data, status=status.HTTP_200_OK)