from rest_framework import serializers
from core.responses import build_absolute_image_url
from .models import Banner


class BannerDiscountSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['id', 'image_url', 'alt_text', 'link', 'expires_at']

    def get_image_url(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)


class BannerSingleSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['id', 'image_url', 'link']

    def get_image_url(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)


class BannerDoubleSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['id', 'image_url', 'link']

    def get_image_url(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)
