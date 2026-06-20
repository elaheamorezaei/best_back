from django.db import models


class Banner(models.Model):
    DISCOUNT_MAIN = 'discount_main'
    SINGLE = 'single'
    DOUBLE = 'double'
    FOOTER_MAIN = 'footer_main'

    BANNER_TYPE_CHOICES = [
        (DISCOUNT_MAIN, 'Discount Main'),
        (SINGLE, 'Single'),
        (DOUBLE, 'Double'),
        (FOOTER_MAIN, 'Footer Main'),
    ]

    banner_type = models.CharField(max_length=20, choices=BANNER_TYPE_CHOICES, db_index=True)
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/')
    mobile_image = models.ImageField(upload_to='banners/mobile/', null=True, blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    link = models.CharField(max_length=500)
    button_text = models.CharField(max_length=100, blank=True)
    expires_at = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.get_banner_type_display()} #{self.id}"
