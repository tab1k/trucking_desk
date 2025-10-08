from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from users.models import User
from .models import Order
from .serializers import OrderReadSerializer, OrderWriteSerializer


class CargoRequestViewSet(ModelViewSet):
    """
    ViewSet для заявок на перевозку. Отправители видят свои заказы,
    водители — назначенные им, администратор — все.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == User.Role.ADMIN or user.is_staff:
            return Order.objects.all().order_by('-created_at')
        if getattr(user, 'role', None) == User.Role.DRIVER:
            return Order.objects.filter(driver=user).order_by('-created_at')
        return Order.objects.filter(sender=user).order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return OrderWriteSerializer
        return OrderReadSerializer

    def create(self, request, *args, **kwargs):
        if getattr(request.user, 'role', None) != User.Role.SENDER:
            raise PermissionDenied('Создавать заявки могут только отправители')
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
