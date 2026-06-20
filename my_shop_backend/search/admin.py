from django.contrib import admin
from .models import TrendingSearch


@admin.register(TrendingSearch)
class TrendingSearchAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_editable = ['order', 'is_active']
