from django.db import models

class TariffSettings(models.Model):
    """Модель для глобальных тарифных настроек."""
    price_per_km = models.DecimalField(max_digits=6, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    base_fee = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = "Tariff Settings"

    def __str__(self):
        return "Тарифные настройки"