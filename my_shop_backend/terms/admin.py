from django.contrib import admin
from .models import Term, TermsMetadata, WalletTermsSection, TermAcceptance


@admin.register(TermsMetadata)
class TermsMetadataAdmin(admin.ModelAdmin):
    list_display = ['version', 'last_updated', 'hero_title']


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'question', 'is_active']
    list_editable = ['order', 'is_active']
    list_display_links = ['id']
    ordering = ['order']


@admin.register(WalletTermsSection)
class WalletTermsSectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'title']
    list_editable = ['order']
    list_display_links = ['id']
    ordering = ['order']


@admin.register(TermAcceptance)
class TermAcceptanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'term_version', 'accepted_at']
    readonly_fields = ['accepted_at']
