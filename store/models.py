from django.db import models
from client.models import Vendor,Customer # For Vendor/User association
from django.utils.translation import gettext_lazy as _

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
    
def get_category_choices():
    """Retrieve all categories as choices for the Product model."""
    try:
        return [(category.name.lower(), category.name) for category in Category.objects.all()]
    except:
        return [] 

class Product(models.Model):
    CATEGORY_CHOICES = get_category_choices()

    title = models.CharField(max_length=255)
    vendor = models.ForeignKey(
        Vendor, 
        on_delete=models.CASCADE, 
        related_name='products', 
        help_text="The vendor who owns this product"
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    sold_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    def is_in_stock(self):       
     return self.stock > 0
    

    

class Favorite(models.Model):
    """
    Model to represent a user's favorite products.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'product')


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
        return cls.objects.filter(user=user.customer, status='CART').first()





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
        return self.product.title

    def get_total_price(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
        self.order.calculate_total_price()
    