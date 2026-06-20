import json
import urllib.request
import urllib.parse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from core.responses import success_response, error_response
from .models import Address
from .serializers import (
    ProfileAddressSerializer, ProfileAddressWriteSerializer,
)


class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        serializer = ProfileAddressSerializer(addresses, many=True)
        return success_response({
            'addresses': serializer.data,
            'total': addresses.count(),
        })

    def post(self, request):
        serializer = ProfileAddressWriteSerializer(
            data=request.data, context={'user': request.user, 'partial': False}
        )
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=422)

        if serializer.validated_data.get('isDefault'):
            Address.objects.filter(user=request.user).update(is_default=False)

        address = serializer.save()
        return Response({
            'success': True,
            'message': 'آدرس با موفقیت ثبت شد',
            'data': {
                'id': address.id,
                'province': address.province,
                'city': address.city,
                'address': address.street,
                'plaque': address.plaque,
                'unit': address.unit,
                'postalCode': address.postal_code,
                'phoneNumber': address.phone_number,
            },
        }, status=201)


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_address(self, request, pk):
        try:
            return Address.objects.get(pk=pk, user=request.user)
        except Address.DoesNotExist:
            return None

    def get(self, request, pk):
        address = self._get_address(request, pk)
        if not address:
            return error_response("آدرس یافت نشد", status=404)
        return success_response(ProfileAddressSerializer(address).data)

    def put(self, request, pk):
        address = self._get_address(request, pk)
        if not address:
            return error_response("آدرس یافت نشد", status=404)

        serializer = ProfileAddressWriteSerializer(
            address, data=request.data,
            context={'user': request.user, 'partial': True}
        )
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=422)

        if serializer.validated_data.get('isDefault'):
            Address.objects.filter(user=request.user).exclude(pk=pk).update(is_default=False)

        serializer.save()
        return Response({'success': True, 'message': 'آدرس با موفقیت ویرایش شد'})

    def delete(self, request, pk):
        address = self._get_address(request, pk)
        if not address:
            return error_response("آدرس یافت نشد", status=404)
        address.delete()
        return Response({'success': True, 'message': 'آدرس با موفقیت حذف شد'})


class GeoSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return error_response("پارامتر q الزامی است", status=400)
        params = urllib.parse.urlencode({'q': q, 'format': 'json', 'limit': 5, 'addressdetails': 1})
        url = f"https://nominatim.openstreetmap.org/search?{params}"
        req = urllib.request.Request(url, headers={'User-Agent': 'MyShopApp/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                results = json.loads(resp.read().decode())
        except Exception:
            return error_response("خطا در سرویس موقعیت‌یابی", status=503)
        data = [
            {
                'displayName': r.get('display_name', ''),
                'lat': float(r.get('lat', 0)),
                'lng': float(r.get('lon', 0)),
            }
            for r in results
        ]
        return success_response({'results': data})
