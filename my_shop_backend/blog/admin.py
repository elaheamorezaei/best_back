from django.contrib import admin
from .models import BlogCategory, BlogPost, BlogBanner, BlogMagazineItem


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'slug', 'name', 'icon']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'views', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    list_editable = ['is_active']
    search_fields = ['title', 'subtitle']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(BlogBanner)
class BlogBannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'alt', 'position', 'is_active']
    list_editable = ['order', 'is_active']


@admin.register(BlogMagazineItem)
class BlogMagazineItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'views', 'is_active', 'created_at']
    list_filter = ['is_active']
    list_editable = ['is_active']
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}
