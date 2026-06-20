from django.db import models


class DeliveryTimeSlot(models.Model):
    label = models.CharField(max_length=50)
    from_time = models.TimeField()
    to_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['from_time']

    def __str__(self):
        return self.label
