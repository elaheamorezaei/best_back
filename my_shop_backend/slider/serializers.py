from rest_framework import serializers
from core.responses import build_absolute_image_url
from .models import Slider


class SliderSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Slider
        fields = ['id', 'title', 'subtitle', 'description', 'image',
                  'cta_text', 'cta_link', 'category']

    def get_image(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)
