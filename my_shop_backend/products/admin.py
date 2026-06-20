from django.contrib import admin
from .models import (
    Category, Product,
    ProductImage, ProductColor, ProductWarranty,
    ProductFeature, ProductSpec, ProductIntro, ProductEditorialReview,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_main', 'parent']
    list_filter = ['is_main']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1


class ProductWarrantyInline(admin.TabularInline):
    model = ProductWarranty
    extra = 1


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 1


class ProductIntroInline(admin.TabularInline):
    model = ProductIntro
    extra = 1


class ProductEditorialReviewInline(admin.StackedInline):
    model = ProductEditorialReview
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'off', 'final_price',
                    'is_featured', 'is_best_seller', 'is_popular', 'stock', 'star']
    list_filter = ['category', 'brand', 'is_featured', 'is_best_seller', 'is_popular']
    search_fields = ['name', 'model', 'brand']
    list_editable = ['is_featured', 'is_best_seller', 'is_popular']
    readonly_fields = ['final_price', 'star', 'created_at']
    inlines = [
        ProductImageInline, ProductColorInline, ProductWarrantyInline,
        ProductFeatureInline, ProductSpecInline, ProductIntroInline,
        ProductEditorialReviewInline,
    ]
