from django.urls import path
from . import views

urlpatterns = [
    path('discount-main/', views.DiscountMainBannerView.as_view(), name='banner-discount-main'),
    path('single/', views.SingleBannerView.as_view(), name='banner-single'),
    path('double/', views.DoubleBannerView.as_view(), name='banner-double'),
    path('footer-main/', views.FooterMainBannerView.as_view(), name='banner-footer-main'),
]
