from django.contrib import admin
from .models import (
    AboutSlider, AboutStoryParagraph, AboutWhyUsItem,
    AboutBranchSection, AboutBranch, AboutDescriptionSection,
    AboutTeamMember, AboutStat,
)


@admin.register(AboutSlider)
class AboutSliderAdmin(admin.ModelAdmin):
    list_display = ['id', 'alt']


@admin.register(AboutStoryParagraph)
class AboutStoryParagraphAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'text']
    list_editable = ['order']
    ordering = ['order']


@admin.register(AboutWhyUsItem)
class AboutWhyUsItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'name', 'icon']
    list_editable = ['order']


@admin.register(AboutBranchSection)
class AboutBranchSectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'alt']


@admin.register(AboutBranch)
class AboutBranchAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'name', 'phone']
    list_editable = ['order']


@admin.register(AboutDescriptionSection)
class AboutDescriptionSectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'title']
    list_editable = ['order']


@admin.register(AboutTeamMember)
class AboutTeamMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'name', 'role']
    list_editable = ['order']


@admin.register(AboutStat)
class AboutStatAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'label', 'value']
    list_editable = ['order']
