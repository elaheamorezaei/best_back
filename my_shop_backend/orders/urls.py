from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:order_id>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:order_id>/retry-payment/', views.PaymentRetryView.as_view(), name='order-retry-payment'),
    path('payment/verify/', views.PaymentVerifyView.as_view(), name='payment-verify'),
    path('payment/methods/', views.PaymentMethodsView.as_view(), name='payment-methods'),

    path('profile/orders/', views.ProfileOrderListView.as_view(), name='profile-order-list'),
    path('profile/orders/<int:order_id>/', views.ProfileOrderDetailView.as_view(), name='profile-order-detail'),
]
