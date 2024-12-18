from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)
from .views import VendorRegisterView, CustomerRegisterView, CustomTokenObtainPairView
# from rest_framework.routers import DefaultRouter


# router = DefaultRouter()




urlpatterns = [
    # path('', include(router.urls)),
    




    path('api/auth/register/vendor/', VendorRegisterView.as_view(), name='vendor-register'),
    path('api/auth/register/customer/', CustomerRegisterView.as_view(), name='customer-register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='TokenObtainPairView'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


]
