from django.urls import path
from . import views

urlpatterns = [
    path('addresses/', views.AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address-detail'),
    path('geo/search/', views.GeoSearchView.as_view(), name='geo-search'),
]
