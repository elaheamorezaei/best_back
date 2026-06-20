from django.urls import path
from . import views

urlpatterns = [
    # Static paths must come before the base compare/ path
    path('compare/products/', views.CompareProductListView.as_view(), name='compare-products'),
    path('compare/description/', views.CompareDescriptionView.as_view(), name='compare-description'),
    path('compare/', views.CompareView.as_view(), name='compare'),
]
