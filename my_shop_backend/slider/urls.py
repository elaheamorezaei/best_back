from django.urls import path
from . import views

urlpatterns = [
    path('', views.SliderListView.as_view(), name='slider-list'),
]
