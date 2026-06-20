from django.contrib import admin
from .models import Wallet, WalletTransaction, WalletIncreaseRequest


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'is_active', 'created_at']
    list_filter = ['is_active']


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'type', 'status', 'tracking_code', 'created_at']
    list_filter = ['type', 'status']


@admin.register(WalletIncreaseRequest)
class WalletIncreaseRequestAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'status', 'created_at', 'expires_at']
    list_filter = ['status']
