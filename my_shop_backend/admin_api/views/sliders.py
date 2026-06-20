from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from admin_api.permissions import IsAdminUser
from slider.models import Slider
from core.responses import build_absolute_image_url


def _serialize_slider(slider, request):
    return {
        'id': slider.id,
        'title': slider.title,
        'subtitle': slider.subtitle,
        'image': build_absolute_image_url(request, slider.image),
        'mobileImage': build_absolute_image_url(request, slider.mobile_image),
        'link': slider.cta_link,
        'buttonText': slider.cta_text,
        'isActive': slider.is_active,
        'order': slider.order,
    }


class AdminSliderListView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        sliders = Slider.objects.all().order_by('order')
        return Response([_serialize_slider(s, request) for s in sliders])

    def post(self, request):
        data = request.data
        title = data.get('title', '').strip()
        if not title:
            return Response({'error': {'message': 'عنوان الزامی است', 'code': 'MISSING_TITLE'}}, status=400)
        if 'image' not in request.FILES:
            return Response({'error': {'message': 'تصویر الزامی است', 'code': 'MISSING_IMAGE'}}, status=400)

        slider = Slider(
            title=title,
            subtitle=data.get('subtitle', ''),
            cta_link=data.get('link', ''),
            cta_text=data.get('buttonText', ''),
            is_active=str(data.get('isActive', 'true')).lower() != 'false',
            order=int(data.get('order', 0)),
            image=request.FILES['image'],
        )
        if 'mobileImage' in request.FILES:
            slider.mobile_image = request.FILES['mobileImage']
        slider.save()
        return Response(_serialize_slider(slider, request), status=201)


class AdminSliderDetailView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get(self, pk):
        try:
            return Slider.objects.get(pk=pk)
        except Slider.DoesNotExist:
            return None

    def patch(self, request, pk):
        slider = self._get(pk)
        if not slider:
            return Response({'error': {'message': 'اسلایدر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        data = request.data
        update_fields = []

        for api_key, model_field in [('title', 'title'), ('subtitle', 'subtitle'),
                                      ('link', 'cta_link'), ('buttonText', 'cta_text')]:
            if api_key in data:
                setattr(slider, model_field, data[api_key])
                update_fields.append(model_field)

        if 'isActive' in data:
            slider.is_active = str(data['isActive']).lower() not in ('false', '0')
            update_fields.append('is_active')

        if 'order' in data:
            slider.order = int(data['order'])
            update_fields.append('order')

        if 'image' in request.FILES:
            slider.image = request.FILES['image']
            update_fields.append('image')

        if 'mobileImage' in request.FILES:
            slider.mobile_image = request.FILES['mobileImage']
            update_fields.append('mobile_image')

        if update_fields:
            slider.save(update_fields=update_fields)

        slider.refresh_from_db()
        return Response(_serialize_slider(slider, request))

    def delete(self, request, pk):
        slider = self._get(pk)
        if not slider:
            return Response({'error': {'message': 'اسلایدر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        slider.delete()
        return Response(status=204)


class AdminSliderReorderView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        items = request.data.get('items', [])
        updated = 0
        for item in items:
            count = Slider.objects.filter(pk=item['id']).update(order=item['order'])
            updated += count
        return Response({'updated': updated})
