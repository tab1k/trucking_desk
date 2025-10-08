from django.db import models
from users.models import User
from locations.models import Location

class CargoType(models.Model):
    """Справочник типов грузов."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    """Основная модель заказа."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Ожидает принятия'
        ACCEPTED = 'ACCEPTED', 'Принят водителем'
        IN_PROGRESS = 'IN_PROGRESS', 'В пути'
        DELIVERED = 'DELIVERED', 'Доставлен'
        CANCELLED = 'CANCELLED', 'Отменен'
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.SENDER}, related_name='sent_orders')
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': User.Role.DRIVER}, related_name='received_orders')
    
    # Маршрут
    departure_point = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='departure_orders')
    destination_point = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='destination_orders')
    
    # Параметры груза
    cargo_type = models.ForeignKey(CargoType, on_delete=models.SET_NULL, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    length = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Расчетные поля
    distance_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_time_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Статус и временные метки
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Флаг для отслеживания геолокации
    is_driver_sharing_location = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['sender', 'created_at']),
        ]

    def __str__(self):
        return f"Заказ #{self.id} от {self.sender}"