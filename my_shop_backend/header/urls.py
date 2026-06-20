from django.urls import path
from . import views

urlpatterns = [
    path('mega-menu/', views.MegaMenuView.as_view(), name='header-mega-menu'),
]
