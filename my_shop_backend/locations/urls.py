from django.urls import path
from . import views

urlpatterns = [
    path('locations/provinces/', views.ProvinceListView.as_view(), name='provinces'),
    path('locations/provinces/<int:province_id>/cities/', views.CityListView.as_view(), name='cities'),
    path('locations/cities/', views.CityListQueryView.as_view(), name='cities-query'),
]
