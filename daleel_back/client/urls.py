from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import VendorRegisterView, CustomerRegisterView, CustomTokenObtainPairView
# from rest_framework.routers import DefaultRouter


# router = DefaultRouter()




urlpatterns = [
    # path('', include(router.urls)),
    




    path('api/auth/register/vendor/', VendorRegisterView.as_view(), name='vendor-register'),
    path('api/auth/register/customer/', CustomerRegisterView.as_view(), name='customer-register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


]
