from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from core.responses import success_response
from .models import Slider
from .serializers import SliderSerializer


class SliderListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        sliders = Slider.objects.filter(is_active=True)
        serializer = SliderSerializer(sliders, many=True, context={'request': request})
        return success_response(serializer.data)
