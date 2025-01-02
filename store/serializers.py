from .models import * 
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name','created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.username', read_only=True)
    class Meta: 
        model = Product
        fields = ['id','title', 'category', 'description', 'stock','price',  'image', 'sold_count','vendor_name', 'created_at']
        read_only_fields = ['vendor', 'sold_count', 'created_at']
    def get_image(self, obj):
        """
        Return the full URL for the image field.
        """
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'category', 'description', 'stock', 'price', 'image', 'vendor', 'sold_count', 'created_at']
        read_only_fields = ['id', 'vendor', 'sold_count', 'created_at']
        
    def create(self, validated_data):
        return Product.objects.create(**validated_data)


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
    product_image = serializers.SerializerMethodField(source='product.image')
    product_category = serializers.StringRelatedField(source='product.category')
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name','product_image', 'vendor_name','product_category', 'quantity', 'price', 'product_price', 'total_price']

    def get_total_price(self, obj):
        return obj.quantity * obj.price
    def get_product_image(self, obj):
        # Fetch the product image URL
        return obj.product.image.url if obj.product and obj.product.image else None




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

class CheckoutSerializer(serializers.ModelSerializer):
    """
    Serializer for the Checkout model.
    """
    order_items = OrderSerializer(read_only=True)
    total_price = serializers.DecimalField(source='order.total_price', read_only=True, max_digits=6, decimal_places=2)
    status = serializers.CharField(source='order.status', read_only=True)

    class Meta:
        model = Checkout
        fields = ['id', 'user', 'order', 'total_price', 'payment_status', 'order_items','status','payment_method', 'shipping_address', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
