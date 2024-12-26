from django.contrib import admin
from .models import * 

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor', 'category', 'price', 'sold_count', 'created_at']
    list_filter = ['vendor', 'category']

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs['choices'] = get_category_choices()
        return super().formfield_for_choice_field(db_field, request, **kwargs)
    
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'created_at']
    search_fields = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [ 'user', 'status', 'total_price','id', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'id']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ( 'product', 'id','get_vendor_name', 'quantity', 'price', 'get_total_price')

    def get_vendor_name(self, obj):
        return obj.product.vendor.username  # Fetch vendor's username
    get_vendor_name.short_description = 'Vendor Name'

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Total Price'


