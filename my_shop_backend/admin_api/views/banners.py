from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from admin_api.permissions import IsAdminUser
from banners.models import Banner
from core.responses import build_absolute_image_url


def _serialize_banner(banner, request):
    return {
        'id': banner.id,
        'title': banner.title,
        'subtitle': banner.subtitle,
        'image': build_absolute_image_url(request, banner.image),
        'mobileImage': build_absolute_image_url(request, banner.mobile_image),
        'link': banner.link,
        'buttonText': banner.button_text,
        'position': banner.banner_type,
        'isActive': banner.is_active,
        'order': banner.order,
        'startDate': banner.start_date.isoformat() if banner.start_date else None,
        'endDate': banner.expires_at.isoformat() if banner.expires_at else None,
    }


class AdminBannerListView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        banners = Banner.objects.all().order_by('order')
        return Response([_serialize_banner(b, request) for b in banners])

    def post(self, request):
        data = request.data
        title = data.get('title', '').strip()
        position = data.get('position', '').strip()

        if not title:
            return Response({'error': {'message': 'عنوان الزامی است', 'code': 'MISSING_TITLE'}}, status=400)
        if 'image' not in request.FILES:
            return Response({'error': {'message': 'تصویر الزامی است', 'code': 'MISSING_IMAGE'}}, status=400)
        if not position:
            return Response({'error': {'message': 'موقعیت الزامی است', 'code': 'MISSING_POSITION'}}, status=400)

        banner = Banner(
            title=title,
            subtitle=data.get('subtitle', ''),
            banner_type=position,
            link=data.get('link', ''),
            button_text=data.get('buttonText', ''),
            is_active=str(data.get('isActive', 'true')).lower() != 'false',
            order=int(data.get('order', 0)),
            image=request.FILES['image'],
        )

        if 'mobileImage' in request.FILES:
            banner.mobile_image = request.FILES['mobileImage']

        import datetime
        start_date = data.get('startDate')
        if start_date:
            try:
                banner.start_date = datetime.date.fromisoformat(start_date)
            except Exception:
                pass

        end_date = data.get('endDate')
        if end_date:
            try:
                banner.expires_at = datetime.date.fromisoformat(end_date)
            except Exception:
                pass

        banner.save()
        return Response(_serialize_banner(banner, request), status=201)


class AdminBannerDetailView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get(self, pk):
        try:
            return Banner.objects.get(pk=pk)
        except Banner.DoesNotExist:
            return None

    def get(self, request, pk):
        banner = self._get(pk)
        if not banner:
            return Response({'error': {'message': 'بنر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        return Response(_serialize_banner(banner, request))

    def patch(self, request, pk):
        banner = self._get(pk)
        if not banner:
            return Response({'error': {'message': 'بنر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        data = request.data
        update_fields = []

        for api_key, model_field in [('title', 'title'), ('subtitle', 'subtitle'), ('link', 'link'),
                                      ('buttonText', 'button_text'), ('position', 'banner_type')]:
            if api_key in data:
                setattr(banner, model_field, data[api_key])
                update_fields.append(model_field)

        if 'isActive' in data:
            banner.is_active = str(data['isActive']).lower() not in ('false', '0')
            update_fields.append('is_active')

        if 'order' in data:
            banner.order = int(data['order'])
            update_fields.append('order')

        if 'image' in request.FILES:
            banner.image = request.FILES['image']
            update_fields.append('image')

        if 'mobileImage' in request.FILES:
            banner.mobile_image = request.FILES['mobileImage']
            update_fields.append('mobile_image')

        import datetime
        if 'startDate' in data:
            try:
                banner.start_date = datetime.date.fromisoformat(data['startDate']) if data['startDate'] else None
                update_fields.append('start_date')
            except Exception:
                pass

        if 'endDate' in data:
            try:
                banner.expires_at = datetime.date.fromisoformat(data['endDate']) if data['endDate'] else None
                update_fields.append('expires_at')
            except Exception:
                pass

        if update_fields:
            banner.save(update_fields=update_fields)

        banner.refresh_from_db()
        return Response(_serialize_banner(banner, request))

    def delete(self, request, pk):
        banner = self._get(pk)
        if not banner:
            return Response({'error': {'message': 'بنر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        banner.delete()
        return Response(status=204)


class AdminBannerReorderView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        items = request.data.get('items', [])
        updated = 0
        for item in items:
            count = Banner.objects.filter(pk=item['id']).update(order=item['order'])
            updated += count
        return Response({'updated': updated})
