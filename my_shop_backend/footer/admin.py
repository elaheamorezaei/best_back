from django.contrib import admin
from .models import (
    SocialLink, CustomerServiceLink, ProductLink,
    AboutUsLink, FeatureBox, PartnerLogo,
)


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'href', 'order']
    list_editable = ['order']


@admin.register(CustomerServiceLink)
class CustomerServiceLinkAdmin(admin.ModelAdmin):
    list_display = ['text', 'href', 'order']
    list_editable = ['order']


@admin.register(ProductLink)
class ProductLinkAdmin(admin.ModelAdmin):
    list_display = ['text', 'href', 'order']
    list_editable = ['order']


@admin.register(AboutUsLink)
class AboutUsLinkAdmin(admin.ModelAdmin):
    list_display = ['text', 'href', 'order']
    list_editable = ['order']


@admin.register(FeatureBox)
class FeatureBoxAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'order']
    list_editable = ['order']


@admin.register(PartnerLogo)
class PartnerLogoAdmin(admin.ModelAdmin):
    list_display = ['alt', 'order']
    list_editable = ['order']
