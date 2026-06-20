from django.db import models


class HeaderItem(models.Model):
    name = models.CharField(max_length=200)
    link = models.CharField(max_length=500)
    icon = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name
