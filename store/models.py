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
    orderstat = models.CharField(
        max_length=20,
        choices=[
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ],
        default="PENDING",
    )
    status = models.CharField(
        max_length=20,
        choices=[
        
        ],
        null=True,
        blank=True,
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Total price of the order"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    def save(self, *args, **kwargs):
        
        self.orderstat = "PENDING"  # Overwrites default
        super().save(*args, **kwargs)

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

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

   

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

class Checkout(models.Model):
    """
    Model to represent the checkout process for an order.
    """
    user = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE,  
        help_text="The user who placed the order",
        related_name="checkouts"
   )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="checkout")
   
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PAID", "Paid"),
            ("FAILED", "Failed"),
        ],
        default="PENDING",
    )
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("INSTAPAY", "InstaPay"),
            ("CASH", "Cash on Delivery"),
        ],
        default="CASH",
    )
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"Checkout for Order {self.order.id} - {self.payment_status}"