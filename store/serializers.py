from .models import * 
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name','created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Product
        fields = ['id','title', 'category', 'description', 'price',  'image', 'sold_count', 'created_at']
        read_only_fields = ['vendor', 'sold_count', 'created_at']



class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Product.
    """
    class Meta:
        model = Product
        fields = ['title', 'description', 'price','stock','image','category']  # Replace with relevant fields


        
    def create(self, validated_data):
        return Product.objects.create(**validated_data)    


# serializers.py

class ProductDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    vendor_name = serializers.CharField(source='vendor.username', read_only=True)
    is_in_stock = serializers.SerializerMethodField()
    total_sold = serializers.IntegerField(source='sold_count', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'stock', 'is_in_stock', 
            'image', 'vendor_name', 'categories', 'total_sold', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'vendor_name', 'categories', 'total_sold', 'created_at', 'updated_at']

    def get_is_in_stock(self, obj):
        return obj.is_in_stock()


class OrderItemSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='product.vendor.username', read_only=True)
    product_name = serializers.CharField(source='product.title', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=6, decimal_places=2)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'vendor_name', 'quantity', 'price', 'product_price', 'total_price']

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

