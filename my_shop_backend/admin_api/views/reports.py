import datetime
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from rest_framework.views import APIView
from rest_framework.response import Response

from admin_api.permissions import IsAdminUser
from orders.models import Order, OrderItem
from products.models import Product
from users.models import UserProfile


def _parse_date(date_str):
    try:
        d = datetime.date.fromisoformat(date_str)
        return timezone.make_aware(datetime.datetime.combine(d, datetime.time.min))
    except Exception:
        return None


class AdminReportSalesView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        data = request.data
        start_date = _parse_date(data.get('startDate', ''))
        end_date = _parse_date(data.get('endDate', ''))
        status_filter = data.get('status', '')
        group_by = data.get('groupBy', 'month')

        qs = Order.objects.filter(
            status__in=[Order.STATUS_PROCESSING, Order.STATUS_SHIPPED, Order.STATUS_DELIVERED]
        )
        if start_date:
            qs = qs.filter(created_at__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__lte=end_date)
        if status_filter:
            qs = qs.filter(status=status_filter)

        if not start_date:
            start_date = timezone.now() - datetime.timedelta(days=365)
        if not end_date:
            end_date = timezone.now()

        PERSIAN_MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                          'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']

        result = []
        current = start_date.date().replace(day=1)
        end = end_date.date().replace(day=1)

        while current <= end:
            if group_by == 'month':
                if current.month == 12:
                    next_period = current.replace(year=current.year + 1, month=1)
                else:
                    next_period = current.replace(month=current.month + 1)
                label = f'{PERSIAN_MONTHS[current.month - 1]} {current.year}'
            else:
                next_period = current + datetime.timedelta(days=1)
                label = current.strftime('%Y-%m-%d')

            period_qs = qs.filter(
                created_at__gte=timezone.make_aware(datetime.datetime.combine(current, datetime.time.min)),
                created_at__lt=timezone.make_aware(datetime.datetime.combine(next_period, datetime.time.min)),
            )
            orders_count = period_qs.count()
            revenue = period_qs.aggregate(t=Sum('final_total'))['t'] or 0
            new_users = UserProfile.objects.filter(
                user__date_joined__gte=timezone.make_aware(datetime.datetime.combine(current, datetime.time.min)),
                user__date_joined__lt=timezone.make_aware(datetime.datetime.combine(next_period, datetime.time.min)),
            ).count()

            result.append({
                'period': label,
                'orders': orders_count,
                'revenue': revenue,
                'averageOrderValue': int(revenue / orders_count) if orders_count else 0,
                'newCustomers': new_users,
            })

            current = next_period

        return Response(result)


class AdminReportProductsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        data = request.data
        start_date = _parse_date(data.get('startDate', ''))
        end_date = _parse_date(data.get('endDate', ''))

        qs = OrderItem.objects.select_related('product__category')
        if start_date:
            qs = qs.filter(order__created_at__gte=start_date)
        if end_date:
            qs = qs.filter(order__created_at__lte=end_date)

        qs = qs.filter(order__status__in=[Order.STATUS_PROCESSING, Order.STATUS_SHIPPED, Order.STATUS_DELIVERED])

        aggregated = (
            qs.values('product_id', 'product_name')
            .annotate(units_sold=Count('id'), revenue=Sum('unit_price'))
            .order_by('-units_sold')[:50]
        )

        result = []
        for item in aggregated:
            prod = Product.objects.filter(pk=item['product_id']).select_related('category').first()
            result.append({
                'productId': item['product_id'],
                'productName': item['product_name'],
                'category': prod.category.name if prod else '',
                'unitsSold': item['units_sold'],
                'revenue': item['revenue'] or 0,
                'returns': 0,
                'currentStock': prod.stock if prod else 0,
            })

        return Response(result)


class AdminReportOrdersView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        data = request.data
        start_date = _parse_date(data.get('startDate', ''))
        end_date = _parse_date(data.get('endDate', ''))
        status_filter = data.get('status', '')

        qs = Order.objects.select_related('user__profile', 'discount_code').prefetch_related('items')
        if start_date:
            qs = qs.filter(created_at__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__lte=end_date)
        if status_filter:
            qs = qs.filter(status=status_filter)

        from admin_api.views.orders import _serialize_order
        return Response([_serialize_order(o, request) for o in qs[:100]])
