from django.contrib import admin
from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'banner_type', 'link', 'is_active', 'order', 'expires_at']
    list_filter = ['banner_type', 'is_active']
    list_editable = ['is_active', 'order']
