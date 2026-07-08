from django.contrib import admin
from .models import FranchiseApplication


@admin.register(FranchiseApplication)
class FranchiseApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'tracking_code', 'full_name', 'phone', 'city', 'province',
        'franchise_type', 'investment_range', 'has_sales_experience', 'created_at',
    ]
    list_filter = ['franchise_type', 'investment_range', 'has_sales_experience', 'province']
    search_fields = ['tracking_code', 'full_name', 'phone', 'email', 'city']
    ordering = ['-created_at']
    readonly_fields = ['tracking_code', 'created_at']
