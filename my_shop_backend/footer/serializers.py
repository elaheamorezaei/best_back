from rest_framework import serializers
from core.responses import build_absolute_image_url
from .models import (
    SocialLink, CustomerServiceLink, ProductLink,
    AboutUsLink, FeatureBox, PartnerLogo,
)


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ['name', 'icon', 'label', 'href']


class CustomerServiceLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerServiceLink
        fields = ['text', 'href']


class ProductLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLink
        fields = ['text', 'href']


class AboutUsLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUsLink
        fields = ['text', 'href']


class FeatureBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureBox
        fields = ['icon', 'title', 'description']


class PartnerLogoSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = PartnerLogo
        fields = ['src', 'alt']

    def get_src(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.src)
