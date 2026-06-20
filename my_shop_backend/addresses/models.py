from django.db import models
from django.conf import settings


class Address(models.Model):
    RECEIVER_SELF = 'self'
    RECEIVER_OTHER = 'other'
    RECEIVER_CHOICES = [(RECEIVER_SELF, 'Self'), (RECEIVER_OTHER, 'Other')]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='addresses', on_delete=models.CASCADE
    )
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=200)
    alley = models.CharField(max_length=200, blank=True)
    plaque = models.CharField(max_length=20)
    unit = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=10)
    receiver_type = models.CharField(max_length=10, choices=RECEIVER_CHOICES, default=RECEIVER_SELF)
    receiver_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    receiver_phone = models.CharField(max_length=15, blank=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    map_address = models.CharField(max_length=500, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.user} — {self.city}, {self.street}"

    @property
    def full_address(self):
        parts = []
        if self.district:
            parts.append(f"خ {self.district}")
        if self.street:
            parts.append(f"خ {self.street}")
        if self.alley:
            parts.append(f"ک {self.alley}")
        plaque_unit = f"پلاک {self.plaque}"
        if self.unit:
            plaque_unit += f" واحد {self.unit}"
        parts.append(plaque_unit)
        return "، ".join(parts)
