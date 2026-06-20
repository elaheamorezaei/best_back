from django.contrib import admin
from .models import (
    ContactInfo, ContactSlider, ContactSubject,
    ContactTicket, ContactTicketAttachment, ContactTicketResponse,
)


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'main_phone', 'support_email']


@admin.register(ContactSlider)
class ContactSliderAdmin(admin.ModelAdmin):
    list_display = ['alt']


@admin.register(ContactSubject)
class ContactSubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'label']
    list_editable = ['order']
    ordering = ['order']


class ContactTicketAttachmentInline(admin.TabularInline):
    model = ContactTicketAttachment
    extra = 0
    readonly_fields = ['file', 'file_type']


class ContactTicketResponseInline(admin.StackedInline):
    model = ContactTicketResponse
    extra = 1
    fields = ['message', 'is_staff', 'staff_name']


@admin.register(ContactTicket)
class ContactTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'subject', 'full_name', 'phone', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['ticket_id', 'full_name', 'email', 'phone']
    readonly_fields = ['ticket_id', 'created_at']
    inlines = [ContactTicketAttachmentInline, ContactTicketResponseInline]
