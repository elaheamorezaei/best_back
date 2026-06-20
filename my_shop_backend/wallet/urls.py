from django.urls import path
from . import views

urlpatterns = [
    path('wallet/', views.WalletView.as_view(), name='wallet'),
    path('wallet/activate/send-otp/', views.WalletActivateSendOTPView.as_view(), name='wallet-activate-send-otp'),
    path('wallet/activate/verify-otp/', views.WalletActivateVerifyOTPView.as_view(), name='wallet-activate-verify-otp'),
    path('wallet/increase/', views.WalletIncreaseView.as_view(), name='wallet-increase'),
    path('wallet/increase/verify/', views.WalletIncreaseVerifyView.as_view(), name='wallet-increase-verify'),
    path('wallet/withdraw/', views.WalletWithdrawView.as_view(), name='wallet-withdraw'),
    path('wallet/transactions/', views.WalletTransactionsView.as_view(), name='wallet-transactions'),
]
