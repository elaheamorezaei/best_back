from django.contrib import admin
from .models import HeaderItem


@admin.register(HeaderItem)
class HeaderItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'link', 'icon', 'order', 'is_active']
    list_editable = ['order', 'is_active']
