from rest_framework import permissions


class UserOrAdminOrReadOnly(permissions.BasePermission):
    """Автор, админ или чтение (для пользователей)."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (obj == request.user and request.user.is_authenticated)
            or request.user.is_staff
        )


class AdminOrAuthorOrReadOnly(permissions.BasePermission):
    """Автор, админ или только чтение (для рецептов)."""

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )
