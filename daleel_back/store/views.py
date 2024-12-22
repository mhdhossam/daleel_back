from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
    CreateAPIView,
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


class ProductListView(ListAPIView):
    """
    API view to retrieve a list of all products sorted by best-selling.
    """
    queryset=Product.objects.all().order_by('-sold_count')
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # No authentication required to view products

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
    queryset = Product.objects.all()

    def get_queryset(self):
        """
        Ensure that vendors can only update their own products.
        """
        user = self.request.user
        if hasattr(user, 'vendor'):  # Check if user is a vendor
            return Product.objects.filter(vendor=user.vendor)
        return Product.objects.none()
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
    queryset = Product.objects.prefetch_related('category').select_related('vendor')
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'  # Use 'slug' if products have slugs




class ProductCreateView(CreateAPIView):
    """
    API view to allow only vendors to create products.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsVendorPermission]
    serializer_class = ProductCreateSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user) 





class AddToCartView(CreateAPIView):
    """
    Add a product to the cart. If a cart doesn't exist, it creates one.
    If the product is already in the cart, it updates the quantity.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = OrderItemSerializer

    def perform_create(self, serializer):
        user = self.request.user
        product_id = self.request.data.get('product_id')
        quantity = int(self.request.data.get('quantity', 1))

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")

        # Get or create cart
        cart = Order.get_cart(user)
        if not cart:
            cart = Order.objects.create(user=user, status='CART')

        # Check if product already exists in the cart
        order_item, created = OrderItem.objects.get_or_create(
            order=cart,
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )

        if not created:
            # Update the quantity if the item already exists
            order_item.quantity += quantity
            order_item.save()

        cart.calculate_total_price()

        return order_item


class RemoveFromCartView(DestroyAPIView):
    """
    Remove a product from the cart.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        # Filter order items by the user's active cart
        user = self.request.user
        cart = Order.get_cart(user)
        if cart:
            return cart.order_items.all()
        return OrderItem.objects.none()

    def destroy(self, request, *args, **kwargs):
        # Perform the deletion and recalculate total price
        instance = self.get_object()
        cart = instance.order
        self.perform_destroy(instance)
        cart.calculate_total_price()

        return Response({"message": "Product removed from cart.", "total_price": cart.total_price})
   


class ViewCartView(RetrieveAPIView):
    """
    View the contents of the cart.
    """
    permission_classes=[IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = OrderSerializer

    def get_object(self):
        user = self.request.user
        cart = Order.get_cart(user)
        if not cart:
            raise serializers.ValidationError("No active cart found.")
        return cart
    