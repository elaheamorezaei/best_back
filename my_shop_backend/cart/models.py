from django.db import models
from django.conf import settings


class InsurancePlan(models.Model):
    name = models.CharField(max_length=200)
    price = models.PositiveIntegerField()
    duration_months = models.PositiveSmallIntegerField(default=12)
    coverages = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    LIST_CURRENT = 'current'
    LIST_NEXT = 'next'
    LIST_CHOICES = [(LIST_CURRENT, 'Current'), (LIST_NEXT, 'Next')]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='cart_items', on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'products.Product', related_name='cart_items', on_delete=models.CASCADE
    )
    color = models.ForeignKey(
        'products.ProductColor', null=True, blank=True, on_delete=models.SET_NULL
    )
    guarantee = models.ForeignKey(
        'products.ProductWarranty', null=True, blank=True, on_delete=models.SET_NULL
    )
    insurance = models.ForeignKey(
        InsurancePlan, null=True, blank=True, on_delete=models.SET_NULL
    )
    quantity = models.PositiveIntegerField(default=1)
    list_type = models.CharField(max_length=10, choices=LIST_CHOICES, default=LIST_CURRENT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user} — {self.product.name} × {self.quantity}"
