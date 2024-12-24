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
    list_display = ['id', 'user', 'status', 'total_price', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'id']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    search_fields = ['order__id', 'product__name']

