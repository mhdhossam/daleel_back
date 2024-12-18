from django.db import models
from client.models import Vendor,Customer # For Vendor/User association


class Product(models.Model):
    name = models.CharField(max_length=255,)
    category= models.ManyToManyField('Category' ,related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)  # Quantity in stock
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    
    vendor = models.ForeignKey(
        Vendor, 
        on_delete=models.CASCADE, 
        related_name='products', 
        help_text="The vendor who owns this product"
    )

  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # For best-selling logic
    sold_count = models.PositiveIntegerField(default=0)  # Number of products sold


   

    class Meta:
        ordering = ['-sold_count', 'name']  # Default ordering by best-sellers and then name
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name

    def is_in_stock(self):
        
        return self.stock > 0
    


class Category(models.Model):


    name = models.CharField(max_length=255,)

    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name="subcategories", null=True, blank=True
    )  # Supports subcategories
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name









class Order(models.Model):
    # Order statuses
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    # Relationships
    user = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='orders', 
        help_text="The user who placed the order"
    )
    products = models.ManyToManyField(
        Product, 
        through='OrderItem', 
        related_name='orders'
    )

    # Order details
    status = models.CharField(
        max_length=20, 
        choices=ORDER_STATUS_CHOICES, 
        default='PENDING',
        help_text="Current status of the order"
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Total price of the order"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    def calculate_total_price(self):
        """
        Calculate and update the total price of the order based on associated OrderItems.
        """
        total = sum(item.get_total_price() for item in self.order_items.all())
        self.total_price = total
        self.save()
    @classmethod
    def get_cart(cls, user):
        return cls.objects.filter(user=user, status='CART').first()





class OrderItem(models.Model):
    """
    Intermediate model for products in an order.
    """
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='order_items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
        self.order.calculate_total_price()
    