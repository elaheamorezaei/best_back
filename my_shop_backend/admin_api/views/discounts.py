from rest_framework.views import APIView
from rest_framework.response import Response

from admin_api.permissions import IsAdminUser
from discounts.models import DiscountCode


def _serialize_discount(d):
    return {
        'id': d.id,
        'code': d.code,
        'type': 'percentage' if d.discount_type == DiscountCode.TYPE_PERCENT else 'fixed',
        'value': d.discount_value,
        'minOrderAmount': d.min_cart_total,
        'maxDiscount': d.max_discount,
        'usageLimit': d.usage_limit,
        'usedCount': d.used_count,
        'perUserLimit': 1,
        'isActive': d.is_active,
        'startDate': None,
        'endDate': d.expires_at.isoformat() if d.expires_at else None,
        'applicableProducts': [],
        'applicableCategories': [],
        'createdAt': None,
    }


class AdminDiscountListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = DiscountCode.objects.all()

        if request.query_params.get('isActive') == 'true':
            qs = qs.filter(is_active=True)
        elif request.query_params.get('isActive') == 'false':
            qs = qs.filter(is_active=False)

        type_filter = request.query_params.get('type')
        if type_filter == 'percentage':
            qs = qs.filter(discount_type=DiscountCode.TYPE_PERCENT)
        elif type_filter == 'fixed':
            qs = qs.filter(discount_type=DiscountCode.TYPE_FIXED)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = max(1, min(100, int(request.query_params.get('pageSize', 20))))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        total = qs.count()
        start = (page - 1) * page_size
        items = list(qs[start:start + page_size])

        return Response({
            'results': [_serialize_discount(d) for d in items],
            'count': total,
            'next': None,
            'previous': None,
        })

    def post(self, request):
        data = request.data
        code = data.get('code', '').strip().upper()
        if not code:
            return Response({'error': {'message': 'کد تخفیف الزامی است', 'code': 'MISSING_CODE'}}, status=400)
        if DiscountCode.objects.filter(code=code).exists():
            return Response({'error': {'message': 'کد تخفیف تکراری است', 'code': 'DUPLICATE_CODE'}}, status=409)

        dtype = DiscountCode.TYPE_PERCENT if data.get('type') == 'percentage' else DiscountCode.TYPE_FIXED

        import datetime
        expires_at = None
        if data.get('endDate'):
            try:
                expires_at = datetime.date.fromisoformat(data['endDate'])
            except Exception:
                pass

        discount = DiscountCode.objects.create(
            code=code,
            discount_type=dtype,
            discount_value=int(data.get('value', 0)),
            min_cart_total=int(data.get('minOrderAmount', 0)),
            max_discount=int(data['maxDiscount']) if data.get('maxDiscount') else None,
            usage_limit=int(data['usageLimit']) if data.get('usageLimit') else None,
            expires_at=expires_at,
            is_active=str(data.get('isActive', 'true')).lower() != 'false',
        )
        return Response(_serialize_discount(discount), status=201)


class AdminDiscountDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get(self, pk):
        try:
            return DiscountCode.objects.get(pk=pk)
        except DiscountCode.DoesNotExist:
            return None

    def get(self, request, pk):
        d = self._get(pk)
        if not d:
            return Response({'error': {'message': 'کد تخفیف یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        return Response(_serialize_discount(d))

    def patch(self, request, pk):
        d = self._get(pk)
        if not d:
            return Response({'error': {'message': 'کد تخفیف یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        data = request.data
        update_fields = []

        if 'value' in data:
            d.discount_value = int(data['value'])
            update_fields.append('discount_value')
        if 'minOrderAmount' in data:
            d.min_cart_total = int(data['minOrderAmount'])
            update_fields.append('min_cart_total')
        if 'maxDiscount' in data:
            d.max_discount = int(data['maxDiscount']) if data['maxDiscount'] else None
            update_fields.append('max_discount')
        if 'usageLimit' in data:
            d.usage_limit = int(data['usageLimit']) if data['usageLimit'] else None
            update_fields.append('usage_limit')
        if 'isActive' in data:
            d.is_active = str(data['isActive']).lower() not in ('false', '0')
            update_fields.append('is_active')
        if 'endDate' in data:
            import datetime
            d.expires_at = datetime.date.fromisoformat(data['endDate']) if data['endDate'] else None
            update_fields.append('expires_at')
        if update_fields:
            d.save(update_fields=update_fields)
        return Response(_serialize_discount(d))

    def delete(self, request, pk):
        d = self._get(pk)
        if not d:
            return Response({'error': {'message': 'کد تخفیف یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        d.delete()
        return Response(status=204)


class AdminDiscountToggleActiveView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            d = DiscountCode.objects.get(pk=pk)
        except DiscountCode.DoesNotExist:
            return Response({'error': {'message': 'کد تخفیف یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        d.is_active = not d.is_active
        d.save(update_fields=['is_active'])
        return Response({'isActive': d.is_active})
