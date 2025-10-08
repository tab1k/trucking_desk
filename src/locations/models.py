from django.db import models

class Location(models.Model):
    """Модель для хранения локаций (городов, точек)."""
    city_name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['city_name']),
        ]

    def __str__(self):
        return self.city_name