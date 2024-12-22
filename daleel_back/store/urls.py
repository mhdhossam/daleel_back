from django.urls import path,include
from.views import( AddToCartView,
                  ViewCartView,
                  RemoveFromCartView,
                  ProductListView,
                  ProductDetailView,
                  ProductCreateView,
                  ProductUpdateView,
                  ProductDeleteView,
                  VendorDashboardView
                  )
# from.payment import CreateInstaPayView, VerifyInstaPayView


urlpatterns = [

    path('api/store/products_all/', ProductListView.as_view(), name='products-all'),
    path('api/store/product/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('api/store/product/create/', ProductCreateView.as_view(), name='product-create'),
    path('api/store/product/update/<int:pk>/', ProductUpdateView.as_view(), name='product-update'),
    path('api/store/product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),
    path('api/vendor/dashboard/', VendorDashboardView.as_view(), name='vendor-dashboard'),
    path('api/store/createorder', AddToCartView.as_view(), name='add-to-cart'),
    path('api/cart/remove/<int:pk>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('api/store/vieworder', ViewCartView.as_view(), name='view-order'),
    #payment
    # path('api/payment/create/', CreateInstaPayView.as_view(), name='payment-create'),
    # path('api/payment/verify/', VerifyInstaPayView.as_view(), name='payment-verify'),



]