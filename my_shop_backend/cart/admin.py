from django.contrib import admin
from .models import InsurancePlan, CartItem


@admin.register(InsurancePlan)
class InsurancePlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'duration_months', 'is_active']
    list_editable = ['is_active']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity', 'list_type', 'created_at']
    list_filter = ['list_type']
    search_fields = ['user__username', 'product__name']
