from django.db import models
from users.models import User
from cargo.models import Order

class Review(models.Model):
    """Модель для отзывов между Водителем и Отправителем."""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['order', 'reviewer']

    def __str__(self):
        return f"Отзыв от {self.reviewer} для {self.reviewed_user}"