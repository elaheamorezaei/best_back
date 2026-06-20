from django.contrib import admin
from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'province', 'city', 'receiver_name', 'is_default']
    list_filter = ['province', 'is_default']
    search_fields = ['receiver_name', 'city', 'street']
