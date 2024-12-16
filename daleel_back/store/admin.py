from django.contrib import admin
from .models import * 

# Register your models here.

@admin.register(Product)

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock','vendor', 'sold_count']
    list_filter = [ 'vendor']
    search_fields = ['name', 'description']




@admin.register(Order)

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'id']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    search_fields = ['order__id', 'product__name']