from django.urls import path,include
from.views import AddToCartView,ViewCartView,RemoveFromCartView


urlpatterns = [



path('api/store/createorder',AddToCartView.as_view(),name='add-to-cart'),
path('api/cart/remove/<int:pk>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
path('api/store/vieworder',ViewCartView.as_view(),name='view-order')




]