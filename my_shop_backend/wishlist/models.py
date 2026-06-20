from django.db import models
from django.conf import settings


class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='wishlists', on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'products.Product', related_name='wishlists', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} → {self.product}"


class StockNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='stock_notifications', on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'products.Product', related_name='stock_notifications', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user} → {self.product} (notify)"
