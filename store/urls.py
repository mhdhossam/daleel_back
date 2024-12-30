from django.urls import path,include
from.views import( AddToCartView,
                  ViewCartView,
                  RemoveFromCartView,
                    UpdateCartView,
                  ProductListView,
                  ProductDetailView,
                  ProductCreateView,
                  ProductUpdateView,
                  ProductDeleteView,
                  VendorDashboardView,
                  WishlistView,
                  AddToWishlistView,
                  RemoveFromWishlistView,
                  CategoryListView,
                  CheckoutView,
                  CheckoutRetrieveAPIView
                  )
# from.payment import CreateInstaPayView, VerifyInstaPayView


urlpatterns = [

    path('api/categories/', CategoryListView.as_view(), name='category-list'),
    path('api/products/', ProductListView.as_view(), name='product-list'),
    path('api/products/<int:id>/', ProductDetailView.as_view(), name='product-detail'),

    path('api/store/product/create/', ProductCreateView.as_view(), name='product-create'),
    path('api/store/product/update/<int:pk>/', ProductUpdateView.as_view(), name='product-update'),
    path('api/store/product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product-delete'),
    path('api/vendor/dashboard/', VendorDashboardView.as_view(), name='vendor-dashboard'),

    path('api/cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('api/cart/remove/<int:pk>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('api/cart/update/<int:pk>/', UpdateCartView.as_view(), name='update-cart'),
    path('api/cart/view/', ViewCartView.as_view(), name='view-cart'),

    path('api/favorites/view/', WishlistView.as_view(), name='view-wishlist'),
    path('api/favorites/add/<int:product_id>/', AddToWishlistView.as_view(), name='add-to-wishlist'),
    path('api/favorites/remove/<int:product_id>/', RemoveFromWishlistView.as_view(), name='remove-from-wishlist'),
    
    path('api/checkout/', CheckoutView.as_view(), name='checkout'),
    path('api/checkout/retrieve/', CheckoutRetrieveAPIView.as_view(), name='checkout-retrieve'),



    #payment
    # path('api/payment/create/', CreateInstaPayView.as_view(), name='payment-create'),
    # path('api/payment/verify/', VerifyInstaPayView.as_view(), name='payment-verify'),



]