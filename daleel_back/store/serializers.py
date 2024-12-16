from .models import * 
from rest_framework import serializers



class ProductSerializer(serializers.ModelSerializer):

    class Meta: 

        model = Product
        fields= '__all__'

        read_only_fields = ['id', 'vendor', 'sold_count', 'is_active', 'created_at', 'updated_at']





class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model, which represents individual products
    in the order.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'product_price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model. It includes nested OrderItemSerializer to handle
    the products inside an order.
    """
    user = serializers.StringRelatedField()  # To display the username (you can customize this field)
    order_items = OrderItemSerializer(many=True, read_only=True)  # Nested OrderItems
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Read-only field

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_items', 'total_price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'total_price', 'created_at', 'updated_at']