from django.urls import path
from . import views

urlpatterns = [
    path('delivery/options/', views.DeliveryOptionsView.as_view(), name='delivery-options'),
    path('delivery/cost/', views.DeliveryCostView.as_view(), name='delivery-cost'),
]
