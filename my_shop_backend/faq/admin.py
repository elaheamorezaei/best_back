from django.contrib import admin
from .models import FAQCategory, FAQ, UserQuestion


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'name', 'icon', 'question_count']
    list_editable = ['order']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'question', 'category', 'helpful_count', 'not_helpful_count', 'is_active']
    list_filter = ['category', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['question', 'answer']


@admin.register(UserQuestion)
class UserQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_id', 'question', 'category', 'email', 'status', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['question', 'email', 'question_id']
    readonly_fields = ['question_id', 'created_at']
