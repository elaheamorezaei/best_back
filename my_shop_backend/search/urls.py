from django.urls import path
from . import views

urlpatterns = [
    path('trending/', views.TrendingSearchView.as_view(), name='search-trending'),
    path('autocomplete/', views.AutocompleteView.as_view(), name='search-autocomplete'),
]
