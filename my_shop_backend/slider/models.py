from django.db import models


class Slider(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='sliders/')
    mobile_image = models.ImageField(upload_to='sliders/mobile/', null=True, blank=True)
    cta_text = models.CharField(max_length=100, blank=True)
    cta_link = models.CharField(max_length=500, blank=True)
    category = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
