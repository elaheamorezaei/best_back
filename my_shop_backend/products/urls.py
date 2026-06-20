from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    # Static paths must come before the router to avoid being matched as {pk}
    path('categories/main/', views.MainCategoryListView.as_view(), name='categories-main'),
    path('products/featured/', views.FeaturedProductsView.as_view(), name='products-featured'),
    path('products/best-sellers/', views.BestSellersView.as_view(), name='products-best-sellers'),
    path('products/most-popular/', views.MostPopularView.as_view(), name='products-most-popular'),
    path('products/compare/', views.ProductCompareView.as_view(), name='products-compare'),
    path('products/<int:pk>/similar/', views.SimilarProductsView.as_view(), name='product-similar'),
    path('products/<int:pk>/compare/', views.ProductCompareDetailView.as_view(), name='product-compare-detail'),
    path('', include(router.urls)),
]
