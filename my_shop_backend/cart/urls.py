from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/items/<int:item_id>/', views.CartItemDetailView.as_view(), name='cart-item'),
    path('cart/items/<int:item_id>/move/', views.CartItemMoveView.as_view(), name='cart-item-move'),
    path('cart/items/<int:item_id>/insurance/', views.CartItemInsuranceView.as_view(), name='cart-item-insurance'),
    path('cart/insurance-plans/', views.InsurancePlansView.as_view(), name='insurance-plans'),
]
