from django.contrib import admin
from .models import DiscountCode, GiftCard


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'used_count', 'usage_limit', 'is_active', 'expires_at']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']


@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ['code', 'balance', 'is_active', 'expires_at']
    list_filter = ['is_active']
    search_fields = ['code']
