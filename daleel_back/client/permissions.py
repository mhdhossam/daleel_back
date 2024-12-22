from rest_framework import permissions


class IsVendorPermission(permissions.BasePermission):
    """
    Custom permission to allow only vendors to create products.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and getattr(request.user, 'is_vendor', True)
