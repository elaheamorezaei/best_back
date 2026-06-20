from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from core.responses import success_response
from .models import Banner
from .serializers import BannerDiscountSerializer, BannerSingleSerializer, BannerDoubleSerializer


class DiscountMainBannerView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        banner = Banner.objects.filter(
            banner_type=Banner.DISCOUNT_MAIN, is_active=True
        ).first()
        if not banner:
            return success_response(None)
        serializer = BannerDiscountSerializer(banner, context={'request': request})
        return success_response(serializer.data)


class SingleBannerView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        banner = Banner.objects.filter(
            banner_type=Banner.SINGLE, is_active=True
        ).first()
        if not banner:
            return success_response(None)
        serializer = BannerSingleSerializer(banner, context={'request': request})
        return success_response(serializer.data)


class DoubleBannerView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        banners = Banner.objects.filter(banner_type=Banner.DOUBLE, is_active=True)
        serializer = BannerDoubleSerializer(banners, many=True, context={'request': request})
        return success_response(serializer.data)


class FooterMainBannerView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        banner = Banner.objects.filter(
            banner_type=Banner.FOOTER_MAIN, is_active=True
        ).first()
        if not banner:
            return success_response(None)
        serializer = BannerSingleSerializer(banner, context={'request': request})
        return success_response(serializer.data)
