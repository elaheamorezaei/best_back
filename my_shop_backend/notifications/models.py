from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_DISCOUNT = 'discount'
    TYPE_INFO = 'info'
    TYPE_WARNING = 'warning'
    TYPE_SYSTEM = 'system'
    TYPE_CHOICES = [
        (TYPE_DISCOUNT, 'تخفیف'),
        (TYPE_INFO, 'اطلاعات'),
        (TYPE_WARNING, 'هشدار'),
        (TYPE_SYSTEM, 'سیستمی'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_INFO)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} — {self.title}"
