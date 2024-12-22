from django.urls import path,include
from.views import AddToCartView,ViewCartView,RemoveFromCartView,ProductDetailView


urlpatterns = [


path('api/products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
# path('api/cart/add/<int:id>/', AddToCartView.as_view(), name='add-to-cart'),
# path('api/cart/remove/<int:id>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
path('api/store/createorder',AddToCartView.as_view(),name='add-to-cart'),
path('api/cart/remove/<int:pk>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
path('api/store/vieworder',ViewCartView.as_view(),name='view-order')




]