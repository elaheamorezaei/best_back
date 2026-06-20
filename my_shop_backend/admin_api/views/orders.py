from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from admin_api.permissions import IsAdminUser
from admin_api.models import OrderNote
from orders.models import Order, OrderItem
from core.utils import to_persian_date


def _serialize_order(order, request=None):
    items = []
    for item in order.items.all():
        image = item.product_image
        if image and request and not image.startswith('http'):
            image = request.build_absolute_uri(image)
        items.append({
            'id': item.id,
            'productId': item.product_id,
            'productName': item.product_name,
            'productImage': image,
            'variant': item.color_name or '',
            'price': item.unit_price,
            'quantity': item.quantity,
            'total': item.unit_price * item.quantity,
        })

    snapshot = order.address_snapshot or {}
    return {
        'id': order.id,
        'orderNumber': order.order_number,
        'status': order.status,
        'paymentStatus': 'paid' if order.paid_at else 'pending',
        'paymentMethod': order.payment_method,
        'customer': {
            'id': order.user_id,
            'name': getattr(getattr(order.user, 'profile', None), 'full_name', order.user.username),
            'email': order.user.email,
            'phone': getattr(getattr(order.user, 'profile', None), 'phone_number', ''),
        },
        'items': items,
        'shippingAddress': {
            'fullName': snapshot.get('receiverName', ''),
            'phone': snapshot.get('phoneNumber', ''),
            'province': snapshot.get('province', ''),
            'city': snapshot.get('city', ''),
            'address': snapshot.get('fullAddress', ''),
            'postalCode': snapshot.get('postalCode', ''),
        },
        'subtotal': order.products_total,
        'shippingCost': order.delivery_cost,
        'discount': order.discount_amount,
        'tax': 0,
        'total': order.final_total,
        'discountCode': order.discount_code.code if order.discount_code else None,
        'trackingCode': order.payment_tracking_code or None,
        'createdAt': order.created_at.isoformat(),
        'updatedAt': order.created_at.isoformat(),
    }


class AdminOrderListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = Order.objects.select_related('user__profile', 'discount_code').prefetch_related('items')

        status = request.query_params.get('status', '').strip()
        if status:
            qs = qs.filter(status=status)

        start_date = request.query_params.get('startDate', '').strip()
        if start_date:
            try:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(start_date)
                if dt:
                    qs = qs.filter(created_at__gte=dt)
            except Exception:
                pass

        end_date = request.query_params.get('endDate', '').strip()
        if end_date:
            try:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(end_date)
                if dt:
                    qs = qs.filter(created_at__lte=dt)
            except Exception:
                pass

        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = max(1, min(100, int(request.query_params.get('pageSize', 20))))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        total = qs.count()
        start = (page - 1) * page_size
        items = list(qs[start:start + page_size])

        return Response({
            'results': [_serialize_order(o, request) for o in items],
            'count': total,
            'next': None,
            'previous': None,
        })


class AdminOrderDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            order = Order.objects.select_related('user__profile', 'discount_code', 'delivery_slot').prefetch_related('items').get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': {'message': 'سفارش یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        return Response(_serialize_order(order, request))

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': {'message': 'سفارش یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        update_fields = []
        if 'status' in request.data:
            order.status = request.data['status']
            update_fields.append('status')
        if 'trackingCode' in request.data:
            order.payment_tracking_code = request.data['trackingCode']
            update_fields.append('payment_tracking_code')

        if update_fields:
            order.save(update_fields=update_fields)

        order.refresh_from_db()
        return Response(_serialize_order(order, request))


class AdminOrderNoteView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': {'message': 'سفارش یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        text = request.data.get('note', '').strip()
        if not text:
            return Response({'error': {'message': 'متن یادداشت الزامی است', 'code': 'MISSING_NOTE'}}, status=400)

        note = OrderNote.objects.create(order=order, author=request.user, text=text, is_admin=True)
        return Response({
            'id': note.id,
            'author': request.user.get_full_name() or 'ادمین',
            'text': note.text,
            'time': note.created_at.isoformat(),
            'isAdmin': note.is_admin,
        })


class AdminOrderCancelView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': {'message': 'سفارش یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=['status'])

        reason = request.data.get('reason', '')
        if reason:
            OrderNote.objects.create(order=order, author=request.user, text=f'لغو: {reason}', is_admin=True)

        order.refresh_from_db()
        return Response(_serialize_order(order, request))


class AdminOrderRefundView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': {'message': 'سفارش یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=['status'])

        amount = request.data.get('amount', order.final_total)
        OrderNote.objects.create(
            order=order, author=request.user,
            text=f'استرداد وجه: {amount} تومان', is_admin=True
        )

        order.refresh_from_db()
        data = _serialize_order(order, request)
        data['paymentStatus'] = 'refunded'
        return Response(data)
