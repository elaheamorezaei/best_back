from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.BlogCategoryListView.as_view(), name='blog-categories'),
    path('posts/', views.BlogPostListView.as_view(), name='blog-posts'),
    path('posts/<int:post_id>/', views.BlogPostDetailView.as_view(), name='blog-post-detail'),
    path('posts/<int:post_id>/view/', views.BlogPostViewIncrementView.as_view(), name='blog-post-view'),
    path('banners/', views.BlogBannerListView.as_view(), name='blog-banners'),
    path('popular/', views.BlogPopularPostsView.as_view(), name='blog-popular'),
    path('magazine/', views.BlogMagazineView.as_view(), name='blog-magazine'),
    path('search/', views.BlogSearchView.as_view(), name='blog-search'),
]
