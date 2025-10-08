from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string

class User(AbstractUser):
    """Расширенная модель пользователя для всех ролей."""
    
    class Role(models.TextChoices):
        DRIVER = 'DRIVER', 'Водитель/Логист'
        SENDER = 'SENDER', 'Отправитель'
        ADMIN = 'ADMIN', 'Администратор'
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SENDER
    )
    phone_number = models.CharField(max_length=20, unique=True)
    # Поля, специфичные для Водителя
    driver_license = models.CharField(max_length=50, blank=True)
    vehicle_type = models.CharField(max_length=100, blank=True)
    vehicle_capacity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_subscription_active = models.BooleanField(default=False)
    # Поля для реферальной системы
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    
    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_referral_code()
        super().save(*args, **kwargs)
    
    def generate_referral_code(self):
        while True:
            code = get_random_string(8).upper()
            if not type(self).objects.filter(referral_code=code).exists():
                return code
            

class DriverLocation(models.Model):
    """Модель для хранения текущей геолокации водителя."""
    driver = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.DRIVER})
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Локация {self.driver}"
