import datetime
from django.utils import timezone
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response

from admin_api.permissions import IsAdminUser
from orders.models import Order
from products.models import Product
from users.models import UserProfile
from contact.models import ContactTicket
from reviews.models import Comment


def _growth(current, previous):
    if not previous:
        return 0.0
    return round((current - previous) / previous * 100, 1)


class DashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()
        start_this = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_prev = (start_this - datetime.timedelta(days=1)).replace(day=1)

        paid_statuses = [Order.STATUS_PAID, Order.STATUS_PROCESSING, Order.STATUS_SHIPPED, Order.STATUS_DELIVERED]

        revenue_this = Order.objects.filter(status__in=paid_statuses, created_at__gte=start_this).aggregate(t=Sum('final_total'))['t'] or 0
        revenue_prev = Order.objects.filter(status__in=paid_statuses, created_at__gte=start_prev, created_at__lt=start_this).aggregate(t=Sum('final_total'))['t'] or 0

        orders_this = Order.objects.filter(created_at__gte=start_this).count()
        orders_prev = Order.objects.filter(created_at__gte=start_prev, created_at__lt=start_this).count()

        products_this = Product.objects.filter(created_at__gte=start_this).count()
        products_prev = Product.objects.filter(created_at__gte=start_prev, created_at__lt=start_this).count()

        users_this = UserProfile.objects.filter(user__date_joined__gte=start_this).count()
        users_prev = UserProfile.objects.filter(user__date_joined__gte=start_prev, user__date_joined__lt=start_this).count()

        return Response({
            'totalRevenue': revenue_this,
            'revenueGrowth': _growth(revenue_this, revenue_prev),
            'totalOrders': Order.objects.count(),
            'ordersGrowth': _growth(orders_this, orders_prev),
            'totalProducts': Product.objects.count(),
            'productsGrowth': _growth(products_this, products_prev),
            'totalUsers': UserProfile.objects.count(),
            'usersGrowth': _growth(users_this, users_prev),
            'pendingOrders': Order.objects.filter(status=Order.STATUS_PENDING).count(),
            'lowStockProducts': Product.objects.filter(stock__lte=5, is_active=True).count(),
            'newMessages': ContactTicket.objects.filter(status=ContactTicket.STATUS_OPEN).count(),
            'pendingReviews': Comment.objects.filter(is_approved=False).count(),
        })


class DashboardRevenueView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        period = request.query_params.get('period', 'month')
        now = timezone.now()
        paid_statuses = [Order.STATUS_PAID, Order.STATUS_PROCESSING, Order.STATUS_SHIPPED, Order.STATUS_DELIVERED]

        PERSIAN_MONTHS = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                          'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        PERSIAN_DAYS = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه']

        result = []

        if period == 'week':
            for i in range(6, -1, -1):
                day = now - datetime.timedelta(days=i)
                start = day.replace(hour=0, minute=0, second=0, microsecond=0)
                end = start + datetime.timedelta(days=1)
                orders_qs = Order.objects.filter(status__in=paid_statuses, created_at__gte=start, created_at__lt=end)
                result.append({
                    'label': PERSIAN_DAYS[day.weekday()],
                    'revenue': orders_qs.aggregate(t=Sum('final_total'))['t'] or 0,
                    'orders': orders_qs.count(),
                })
        elif period == 'month':
            for m in range(11, -1, -1):
                first = (now.replace(day=1) - datetime.timedelta(days=m * 28)).replace(day=1)
                if m == 0:
                    last = now
                else:
                    last = (first.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
                orders_qs = Order.objects.filter(status__in=paid_statuses, created_at__gte=first, created_at__lt=last)
                result.append({
                    'label': PERSIAN_MONTHS[first.month - 1],
                    'revenue': orders_qs.aggregate(t=Sum('final_total'))['t'] or 0,
                    'orders': orders_qs.count(),
                })
        else:
            for y in range(now.year - 2, now.year + 1):
                start = timezone.datetime(y, 1, 1, tzinfo=now.tzinfo)
                end = timezone.datetime(y + 1, 1, 1, tzinfo=now.tzinfo)
                orders_qs = Order.objects.filter(status__in=paid_statuses, created_at__gte=start, created_at__lt=end)
                result.append({
                    'label': str(y),
                    'revenue': orders_qs.aggregate(t=Sum('final_total'))['t'] or 0,
                    'orders': orders_qs.count(),
                })

        return Response(result)


class DashboardTopProductsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        from django.db.models import Sum as DSum
        from orders.models import OrderItem
        items = (
            OrderItem.objects
            .values('product_id', 'product_name')
            .annotate(sales=Count('id'), revenue=DSum('unit_price'))
            .order_by('-sales')[:5]
        )
        result = []
        for item in items:
            prod = Product.objects.filter(pk=item['product_id']).first()
            result.append({
                'id': item['product_id'],
                'name': item['product_name'],
                'image': request.build_absolute_uri(prod.image.url) if prod and prod.image else None,
                'sales': item['sales'],
                'revenue': item['revenue'] or 0,
            })
        return Response(result)


class DashboardRecentOrdersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        orders = Order.objects.select_related('user__profile').order_by('-created_at')[:5]
        result = []
        for order in orders:
            profile = getattr(order.user, 'profile', None)
            result.append({
                'id': order.id,
                'orderNumber': order.order_number,
                'customerName': profile.full_name if profile else order.user.username,
                'total': order.final_total,
                'status': order.status,
                'createdAt': order.created_at.isoformat(),
            })
        return Response(result)
