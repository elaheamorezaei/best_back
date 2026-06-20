from django.contrib import admin
from .models import UserProfile, OTPCode, LoginAttempt, PasswordResetSession


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'full_name', 'user']
    search_fields = ['phone_number', 'full_name', 'user__username']


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'code', 'purpose', 'is_used', 'expires_at', 'created_at']
    list_filter = ['purpose', 'is_used']
    search_fields = ['phone_number']
    readonly_fields = ['created_at']


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'attempts', 'is_locked', 'locked_until']
    search_fields = ['phone_number']
    readonly_fields = ['last_attempt_at']


@admin.register(PasswordResetSession)
class PasswordResetSessionAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'step', 'is_used', 'expires_at', 'created_at']
    list_filter = ['step', 'is_used']
    search_fields = ['phone_number']
    readonly_fields = ['created_at']
