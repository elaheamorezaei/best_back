from django.contrib import admin
from .models import Slider


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'category', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title']
