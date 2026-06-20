from django.contrib import admin
from .models import Province, City


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'province']
    list_filter = ['province']
    search_fields = ['name']
