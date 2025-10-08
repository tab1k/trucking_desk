from django.db import models
from users.models import User

class SubscriptionPlan(models.Model):
    """Модель для тарифных планов подписки."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class UserSubscription(models.Model):
    """Активные подписки пользователей."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.DRIVER})
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.plan}"