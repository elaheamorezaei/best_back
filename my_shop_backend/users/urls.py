from django.urls import path
from . import views

urlpatterns = [
    path('auth/phone/', views.PhoneCheckView.as_view(), name='auth-phone'),
    path('auth/login/password/', views.LoginPasswordView.as_view(), name='auth-login-password'),
    path('auth/otp/send/', views.OTPSendView.as_view(), name='auth-otp-send'),
    path('auth/otp/verify/', views.OTPVerifyView.as_view(), name='auth-otp-verify'),
    path('auth/forgot-password/send-otp/', views.ForgotPasswordSendOTPView.as_view(), name='auth-forgot-send-otp'),
    path('auth/forgot-password/verify-otp/', views.ForgotPasswordVerifyOTPView.as_view(), name='auth-forgot-verify-otp'),
    path('auth/forgot-password/reset/', views.ForgotPasswordResetView.as_view(), name='auth-forgot-reset'),
    path('auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('auth/refresh/', views.TokenRefreshView.as_view(), name='auth-refresh'),

    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/avatar/', views.AvatarUploadView.as_view(), name='profile-avatar'),
    path('profile/password/', views.PasswordChangeView.as_view(), name='profile-password'),
]
