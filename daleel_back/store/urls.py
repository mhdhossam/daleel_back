from django.urls import path,include
from.views import AddToCartView,ViewCartView


urlpatterns = [

path('api/store/createorder',AddToCartView.as_view(),name='add-to-cart'),

path('api/store/vieworder',ViewCartView.as_view(),name='view-order')




]