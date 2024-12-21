from rest_framework.generics import (
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
)
from rest_framework.response import Response
from rest_framework import status
from.models import * 
from.serializers import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated



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
    