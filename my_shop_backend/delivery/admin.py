from django.contrib import admin
from .models import DeliveryTimeSlot


@admin.register(DeliveryTimeSlot)
class DeliveryTimeSlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'label', 'from_time', 'to_time', 'is_active']
    list_editable = ['is_active']
