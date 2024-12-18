from .models import * 
from rest_framework import serializers



class ProductSerializer(serializers.ModelSerializer):

    class Meta: 

        model = Product
        fields= '__all__'

        read_only_fields = ['id', 'vendor', 'sold_count', 'is_active', 'created_at', 'updated_at']




class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name','created_at']
        read_only_fields = ['id', 'created_at']






class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model, which represents individual products
    in the order.
    """
    vendor_name = serializers.CharField(source='product.vendor.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True , max_digits=6 , decimal_places=2,)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Read-only field

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'vendor_name' ,'quantity', 'price', 'product_price', 'total_price']
        
    def get_total_price(self, obj):
        return obj.quantity * obj.price



class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model. It includes nested OrderItemSerializer to handle
    the products inside an order.
    """
    user = serializers.StringRelatedField()  # To display the username (you can customize this field)
    order_items = OrderItemSerializer(many=True, read_only=True)  # Nested OrderItems
    

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_items', 'total_price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'total_price', 'created_at', 'updated_at']

