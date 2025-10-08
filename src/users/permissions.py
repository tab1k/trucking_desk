from rest_framework import permissions
from .models import User

class IsAdminOrSelf(permissions.BasePermission):
    """Разрешает полный доступ администраторам и работу только со своим профилем остальным пользователям."""

    @staticmethod
    def _is_admin(user):
        return user.is_staff or user.is_superuser or getattr(user, 'role', None) == User.Role.ADMIN

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        action = getattr(view, 'action', None)
        if action in ['list', 'create']:
            return self._is_admin(user)
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if self._is_admin(user):
            return True
        return obj == user
