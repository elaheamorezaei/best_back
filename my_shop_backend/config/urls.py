from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def health_check(request):
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('health/', health_check),
    path('admin/', admin.site.urls),

    path('api/v1/banners/', include('banners.urls')),
    path('api/v1/search/', include('search.urls')),
    path('api/v1/header/', include('header.urls')),
    path('api/v1/slider/', include('slider.urls')),
    path('api/v1/blog/', include('blog.urls')),
    path('api/v1/footer/', include('footer.urls')),
    path('api/v1/', include('products.urls')),
    path('api/v1/', include('reviews.urls')),
    path('api/v1/', include('wishlist.urls')),
    path('api/v1/', include('cart.urls')),
    path('api/v1/', include('addresses.urls')),
    path('api/v1/', include('delivery.urls')),
    path('api/v1/', include('discounts.urls')),
    path('api/v1/', include('locations.urls')),
    path('api/v1/', include('orders.urls')),
    path('api/v1/', include('about.urls')),
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('contact.urls')),
    path('api/v1/', include('faq.urls')),
    path('api/v1/', include('notifications.urls')),
    path('api/v1/', include('wallet.urls')),
    path('api/v1/', include('terms.urls')),
    path('api/v1/', include('compare.urls')),
    path('api/v1/', include('admin_api.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
