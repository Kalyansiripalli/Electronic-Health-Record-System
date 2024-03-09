from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user associated with the JWT token is an admin
        return request.user and request.user.is_authenticated and request.user.is_admin
