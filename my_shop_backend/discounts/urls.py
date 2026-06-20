from django.urls import path
from . import views

urlpatterns = [
    path('discounts/validate/', views.DiscountCodeValidateView.as_view(), name='discount-validate'),
    path('gift-cards/validate/', views.GiftCardValidateView.as_view(), name='gift-card-validate'),
]
