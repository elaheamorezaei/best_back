from django.contrib import admin
from .models import CompareDescription


@admin.register(CompareDescription)
class CompareDescriptionAdmin(admin.ModelAdmin):
    list_display = ['category', 'title']
    search_fields = ['category__name', 'title']
