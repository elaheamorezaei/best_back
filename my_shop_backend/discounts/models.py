from django.db import models


class DiscountCode(models.Model):
    TYPE_PERCENT = 'percent'
    TYPE_FIXED = 'fixed'
    TYPE_CHOICES = [(TYPE_PERCENT, 'Percent'), (TYPE_FIXED, 'Fixed')]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    discount_value = models.PositiveIntegerField()
    max_discount = models.PositiveIntegerField(null=True, blank=True)
    min_cart_total = models.PositiveIntegerField(default=0)
    expires_at = models.DateField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def calc_discount(self, cart_total):
        if self.discount_type == self.TYPE_PERCENT:
            amount = int(cart_total * self.discount_value / 100)
            if self.max_discount:
                amount = min(amount, self.max_discount)
        else:
            amount = min(self.discount_value, cart_total)
        return amount


class GiftCard(models.Model):
    code = models.CharField(max_length=50, unique=True)
    balance = models.PositiveIntegerField()
    expires_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
