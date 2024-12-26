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




class UpdateCartView(UpdateAPIView):
    """
    Update the quantity of a product in the cart.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        user = self.request.user
        cart = Order.get_cart(user)
        if not cart:
            raise serializers.ValidationError("No active cart found.")
        return OrderItem.objects.filter(order=cart)

    def perform_update(self, serializer):
        quantity = int(self.request.data.get('quantity', 1))

        if quantity <= 0:
            serializer.instance.delete()
        else:
            serializer.save(quantity=quantity)

        # Recalculate cart total price
        cart = serializer.instance.order
        cart.calculate_total_price()



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
    




class AddToFavoritesView(APIView):
    """
    API view to add a product to the user's favorites.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

        if not created:
            return Response({"message": "Product is already in favorites."}, status=status.HTTP_200_OK)

        return Response({"message": "Product added to favorites."}, status=status.HTTP_201_CREATED)
    