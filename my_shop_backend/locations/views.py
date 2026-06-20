from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Province
from .serializers import ProvinceSerializer, CitySerializer
from core.responses import success_response, error_response


class ProvinceListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        provinces = Province.objects.all()
        serializer = ProvinceSerializer(provinces, many=True)
        return success_response({'provinces': serializer.data})


class CityListView(APIView):
    """GET /locations/provinces/{province_id}/cities/ (legacy path-param form)"""
    permission_classes = [AllowAny]

    def get(self, request, province_id):
        try:
            province = Province.objects.prefetch_related('cities').get(pk=province_id)
        except Province.DoesNotExist:
            return error_response("استان یافت نشد", status=404)
        serializer = CitySerializer(province.cities.all(), many=True)
        return success_response({'cities': serializer.data})


class CityListQueryView(APIView):
    """GET /locations/cities/?provinceId={id} (query-param form used by profile spec)"""
    permission_classes = [AllowAny]

    def get(self, request):
        province_id = request.query_params.get('provinceId', '').strip()
        if not province_id:
            return error_response("پارامتر provinceId الزامی است", status=400)
        try:
            province = Province.objects.prefetch_related('cities').get(pk=int(province_id))
        except (Province.DoesNotExist, ValueError):
            return error_response("استان یافت نشد", status=404)
        serializer = CitySerializer(province.cities.all(), many=True)
        return success_response({'cities': serializer.data})
