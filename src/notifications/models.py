from django.db import models
from users.models import User
from cargo.models import Order

class Notification(models.Model):
    """Модель для уведомлений."""
    class Type(models.TextChoices):
        NEW_ORDER = 'NEW_ORDER', 'Новый заказ'
        ORDER_ACCEPTED = 'ORDER_ACCEPTED', 'Заказ принят'
        ORDER_DELIVERED = 'ORDER_DELIVERED', 'Заказ доставлен'
        SUBSCRIPTION_EXPIRING = 'SUBSCRIPTION_EXPIRING', 'Подписка истекает'
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"Уведомление для {self.user}"