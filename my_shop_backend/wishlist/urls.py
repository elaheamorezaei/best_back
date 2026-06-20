from django.urls import path
from . import views

urlpatterns = [
    path('products/<int:product_id>/wishlist/', views.WishlistToggleView.as_view(), name='product-wishlist'),
    path('products/<int:product_id>/notify/', views.StockNotifyView.as_view(), name='product-notify'),

    path('profile/favorites/', views.FavoritesView.as_view(), name='profile-favorites'),
    path('profile/favorites/<int:favorite_id>/', views.FavoriteDeleteView.as_view(), name='profile-favorites-delete'),
]
