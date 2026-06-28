import uuid
import datetime
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.responses import success_response, error_response
from .models import Order, OrderItem
from cart.models import CartItem
from addresses.models import Address
from delivery.views import DELIVERY_COSTS
from discounts.models import DiscountCode, GiftCard
from delivery.models import DeliveryTimeSlot
from core.utils import to_persian_date


def _generate_order_number():
    return uuid.uuid4().hex[:12].upper()


def _serialize_order(order, request=None):
    items_data = []
    for item in order.items.all():
        image_url = item.product_image
        if image_url and request:
            if not image_url.startswith('http'):
                image_url = request.build_absolute_uri(image_url)
        items_data.append({
            'id': item.id,
            'productId': item.product_id,
            'productName': item.product_name,
            'productImage': image_url,
            'colorName': item.color_name,
            'guaranteeText': item.guarantee_text,
            'quantity': item.quantity,
            'unitPrice': item.unit_price,
            'insuranceName': item.insurance_name,
            'insurancePrice': item.insurance_price,
        })
    return {
        'id': order.id,
        'orderNumber': order.order_number,
        'status': order.status,
        'address': order.address_snapshot,
        'deliveryType': order.delivery_type,
        'deliveryDate': order.delivery_date,
        'deliveryCost': order.delivery_cost,
        'paymentMethod': order.payment_method,
        'paymentTrackingCode': order.payment_tracking_code,
        'productsTotal': order.products_total,
        'insuranceTotal': order.insurance_total,
        'discountAmount': order.discount_amount,
        'discountCodeAmount': order.discount_code_amount,
        'giftCardAmount': order.gift_card_amount,
        'finalTotal': order.final_total,
        'createdAt': to_persian_date(order.created_at),
        'items': items_data,
    }


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        # --- Validate address ---
        address_id = data.get('addressId')
        if not address_id:
            return error_response("آدرس تحویل الزامی است", status=400)
        try:
            address = Address.objects.get(pk=address_id, user=request.user)
        except Address.DoesNotExist:
            return error_response("آدرس یافت نشد", status=404)

        # --- Validate delivery ---
        delivery_type = data.get('deliveryType', 'normal')
        if delivery_type not in DELIVERY_COSTS:
            return error_response("نوع ارسال نامعتبر است", status=400)
        delivery_date = data.get('deliveryDate', '')
        delivery_slot_id = data.get('deliverySlotId')
        delivery_slot = None
        if delivery_slot_id:
            try:
                delivery_slot = DeliveryTimeSlot.objects.get(pk=delivery_slot_id, is_active=True)
            except DeliveryTimeSlot.DoesNotExist:
                return error_response("بازه زمانی ارسال یافت نشد", status=404)
        delivery_cost = DELIVERY_COSTS[delivery_type]

        # --- Validate payment method ---
        payment_method = data.get('paymentMethod', Order.PAYMENT_ONLINE)
        if payment_method not in (Order.PAYMENT_ONLINE, Order.PAYMENT_COD):
            return error_response("روش پرداخت نامعتبر است", status=400)

        # --- Cart items ---
        cart_items = list(CartItem.objects.filter(
            user=request.user, list_type=CartItem.LIST_CURRENT
        ).select_related('product', 'color', 'guarantee', 'insurance'))
        if not cart_items:
            return error_response("سبد خرید خالی است", status=400)

        # --- Validate stock ---
        for ci in cart_items:
            if not ci.product.in_stock or ci.product.stock < ci.quantity:
                return error_response(f"موجودی محصول «{ci.product.name}» کافی نیست", status=400)

        # --- Calculate totals ---
        products_total = sum(ci.product.final_price * ci.quantity for ci in cart_items)
        insurance_total = sum(
            (ci.insurance.price if ci.insurance else 0) * ci.quantity for ci in cart_items
        )
        subtotal = products_total + insurance_total

        # Discount code
        discount_code_obj = None
        discount_code_amount = 0
        discount_code_str = data.get('discountCode', '').strip()
        if discount_code_str:
            try:
                discount_code_obj = DiscountCode.objects.get(code=discount_code_str, is_active=True)
                if not (discount_code_obj.expires_at and discount_code_obj.expires_at < datetime.date.today()):
                    if not (discount_code_obj.usage_limit and discount_code_obj.used_count >= discount_code_obj.usage_limit):
                        if subtotal >= discount_code_obj.min_cart_total:
                            discount_code_amount = discount_code_obj.calc_discount(subtotal)
            except DiscountCode.DoesNotExist:
                pass

        # Gift card
        gift_card_obj = None
        gift_card_amount = 0
        gift_card_str = data.get('giftCardCode', '').strip()
        if gift_card_str:
            try:
                gift_card_obj = GiftCard.objects.get(code=gift_card_str, is_active=True)
                if not (gift_card_obj.expires_at and gift_card_obj.expires_at < datetime.date.today()):
                    gift_card_amount = min(gift_card_obj.balance, subtotal - discount_code_amount)
            except GiftCard.DoesNotExist:
                pass

        discount_amount = discount_code_amount + gift_card_amount
        final_total = max(0, subtotal + delivery_cost - discount_amount)

        # --- Build address snapshot ---
        address_snapshot = {
            'province': address.province,
            'city': address.city,
            'fullAddress': address.full_address,
            'postalCode': address.postal_code,
            'receiverName': address.receiver_name,
            'phoneNumber': address.phone_number,
            'receiverPhone': address.receiver_phone,
        }

        # --- Create order ---
        order = Order.objects.create(
            user=request.user,
            order_number=_generate_order_number(),
            address=address,
            address_snapshot=address_snapshot,
            delivery_type=delivery_type,
            delivery_date=delivery_date,
            delivery_slot=delivery_slot,
            delivery_cost=delivery_cost,
            payment_method=payment_method,
            discount_code=discount_code_obj,
            gift_card=gift_card_obj,
            products_total=products_total,
            insurance_total=insurance_total,
            discount_amount=discount_amount,
            discount_code_amount=discount_code_amount,
            gift_card_amount=gift_card_amount,
            final_total=final_total,
            status=Order.STATUS_PENDING,
        )

        # --- Create order items ---
        for ci in cart_items:
            product_image = ''
            first_img = ci.product.images.first()
            if first_img:
                try:
                    product_image = first_img.image.url
                except Exception:
                    pass
            elif ci.product.image:
                try:
                    product_image = ci.product.image.url
                except Exception:
                    pass

            OrderItem.objects.create(
                order=order,
                product=ci.product,
                product_name=ci.product.name,
                product_image=product_image,
                color_name=ci.color.name if ci.color else '',
                guarantee_text=ci.guarantee.text if ci.guarantee else '',
                quantity=ci.quantity,
                unit_price=ci.product.final_price,
                insurance_name=ci.insurance.name if ci.insurance else '',
                insurance_price=ci.insurance.price if ci.insurance else 0,
            )

        # Decrease stock
        for ci in cart_items:
            ci.product.stock -= ci.quantity
            ci.product.save(update_fields=['stock'])

        # Increment discount code usage
        if discount_code_obj:
            discount_code_obj.used_count += 1
            discount_code_obj.save(update_fields=['used_count'])

        # Clear cart
        CartItem.objects.filter(user=request.user, list_type=CartItem.LIST_CURRENT).delete()

        # For COD orders, mark as paid immediately
        if payment_method == Order.PAYMENT_COD:
            order.status = Order.STATUS_PROCESSING
            order.paid_at = timezone.now()
            order.save(update_fields=['status', 'paid_at'])
            return success_response({
                'orderId': order.id,
                'orderNumber': order.order_number,
                'paymentMethod': 'cod',
                'status': order.status,
            }, status=201)

        # For online payment, generate a fake payment token
        payment_token = uuid.uuid4().hex
        order.payment_token = payment_token
        order.save(update_fields=['payment_token'])

        return success_response({
            'orderId': order.id,
            'orderNumber': order.order_number,
            'paymentMethod': 'online',
            'paymentToken': payment_token,
            'paymentUrl': f"/api/v1/payment/gateway/?token={payment_token}",
            'amount': final_total,
        }, status=201)


class PaymentVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token', '').strip()
        if not token:
            return error_response("توکن پرداخت الزامی است", status=400)
        try:
            order = Order.objects.get(payment_token=token, user=request.user)
        except Order.DoesNotExist:
            return error_response("سفارش یافت نشد", status=404)

        if order.status != Order.STATUS_PENDING:
            return error_response("وضعیت سفارش برای تأیید پرداخت مناسب نیست", status=400)

        # Simulate payment verification — always success in sandbox
        tracking_code = uuid.uuid4().hex[:10].upper()
        order.status = Order.STATUS_PROCESSING
        order.payment_tracking_code = tracking_code
        order.paid_at = timezone.now()
        order.save(update_fields=['status', 'payment_tracking_code', 'paid_at'])

        return success_response({
            'orderId': order.id,
            'orderNumber': order.order_number,
            'trackingCode': tracking_code,
            'status': order.status,
        })


class PaymentRetryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id, user=request.user)
        except Order.DoesNotExist:
            return error_response("سفارش یافت نشد", status=404)

        if order.status != Order.STATUS_FAILED:
            return error_response("امکان تلاش مجدد برای این سفارش وجود ندارد", status=400)

        new_token = uuid.uuid4().hex
        order.payment_token = new_token
        order.status = Order.STATUS_PENDING
        order.save(update_fields=['payment_token', 'status'])

        return success_response({
            'orderId': order.id,
            'orderNumber': order.order_number,
            'paymentToken': new_token,
            'paymentUrl': f"/api/v1/payment/gateway/?token={new_token}",
            'amount': order.final_total,
        })


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.prefetch_related('items__product').get(
                pk=order_id, user=request.user
            )
        except Order.DoesNotExist:
            return error_response("سفارش یافت نشد", status=404)
        return success_response(_serialize_order(order, request))


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
        return success_response([_serialize_order(o, request) for o in orders])


class PaymentMethodsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response([
            {'id': 'online', 'label': 'پرداخت آنلاین', 'description': 'پرداخت از طریق درگاه بانکی'},
            {'id': 'cod', 'label': 'پرداخت در محل', 'description': 'پرداخت نقدی هنگام تحویل'},
        ])


# ---------------------------------------------------------------------------
# Profile order views  (GET /profile/orders, GET /profile/orders/{id})
# ---------------------------------------------------------------------------

_STATUS_INT_MAP = {
    'pending_payment': (1, 'در حال پرداخت'),
    'paid':            (1, 'در حال پرداخت'),
    'processing':      (1, 'در حال پرداخت'),
    'shipped':         (2, 'ارسال شده'),
    'delivered':       (3, 'تحویل داده شده'),
    'cancelled':       (4, 'لغو شده'),
    'payment_failed':  (4, 'لغو شده'),
}

_STATUS_FILTER_MAP = {
    '1': ['pending_payment', 'paid', 'processing'],
    '2': ['shipped'],
    '3': ['delivered'],
    '4': ['cancelled', 'payment_failed'],
}

_DELIVERY_LABELS = {
    'normal': 'ارسال عادی',
    'express': 'ارسال اکسپرس',
    'same_day': 'ارسال همان روز',
}

_PAYMENT_LABELS = {
    'online': 'پرداخت اینترنتی',
    'cod': 'پرداخت در محل',
}


def _jalali_to_date(jalali_str):
    try:
        import jdatetime
        import datetime
        from django.utils import timezone as tz
        y, m, d = map(int, jalali_str.split('/'))
        g = jdatetime.date(y, m, d).togregorian()
        return tz.make_aware(datetime.datetime.combine(g, datetime.time.min))
    except Exception:
        return None


class ProfileOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Order.objects.filter(user=request.user).prefetch_related('items')

        status_filter = request.query_params.get('status', '').strip()
        if status_filter in _STATUS_FILTER_MAP:
            qs = qs.filter(status__in=_STATUS_FILTER_MAP[status_filter])

        from_date = request.query_params.get('fromDate', '').strip()
        if from_date:
            dt = _jalali_to_date(from_date)
            if dt:
                qs = qs.filter(created_at__gte=dt)

        to_date = request.query_params.get('toDate', '').strip()
        if to_date:
            dt = _jalali_to_date(to_date)
            if dt:
                from django.utils import timezone as tz
                import datetime
                end = tz.make_aware(datetime.datetime.combine(dt.date(), datetime.time.max))
                qs = qs.filter(created_at__lte=end)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1
        try:
            limit = max(1, min(50, int(request.query_params.get('limit', 10))))
        except (ValueError, TypeError):
            limit = 10

        total = qs.count()
        import math
        total_pages = math.ceil(total / limit) if total else 1
        orders = list(qs[(page - 1) * limit: page * limit])

        order_list = []
        for row_idx, order in enumerate(orders, start=(page - 1) * limit + 1):
            status_int, status_label = _STATUS_INT_MAP.get(order.status, (1, order.status))
            items = []
            for item in order.items.all():
                image_url = item.product_image or None
                if image_url and not image_url.startswith('http'):
                    image_url = request.build_absolute_uri(image_url)
                items.append({
                    'productId': item.product_id,
                    'name': item.product_name,
                    'image': image_url,
                    'quantity': item.quantity,
                })
            order_list.append({
                'id': order.id,
                'row': row_idx,
                'date': to_persian_date(order.created_at),
                'orderNumber': order.order_number,
                'amount': f"{order.final_total} تومان",
                'status': status_int,
                'statusLabel': status_label,
                'items': items,
            })

        return success_response({
            'orders': order_list,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'totalPages': total_pages,
            },
        })


class ProfileOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.prefetch_related('items').select_related('delivery_slot').get(
                pk=order_id, user=request.user
            )
        except Order.DoesNotExist:
            return error_response("سفارش یافت نشد", status=404)

        status_int, status_label = _STATUS_INT_MAP.get(order.status, (1, order.status))

        items = []
        for item in order.items.all():
            image_url = item.product_image or None
            if image_url and not image_url.startswith('http'):
                image_url = request.build_absolute_uri(image_url)
            items.append({
                'productId': item.product_id,
                'name': item.product_name,
                'image': image_url,
                'color': item.color_name or None,
                'guarantee': item.guarantee_text or None,
                'quantity': item.quantity,
                'unitPrice': item.unit_price,
            })

        snapshot = order.address_snapshot or {}
        address_data = {
            'province': snapshot.get('province', ''),
            'city': snapshot.get('city', ''),
            'fullAddress': snapshot.get('fullAddress', ''),
            'postalCode': snapshot.get('postalCode', ''),
            'receiverName': snapshot.get('receiverName', ''),
            'phoneNumber': snapshot.get('phoneNumber', ''),
            'receiverPhone': snapshot.get('receiverPhone', ''),
        }

        delivery_data = {
            'type': _DELIVERY_LABELS.get(order.delivery_type, order.delivery_type),
            'date': order.delivery_date or None,
            'timeSlot': order.delivery_slot.label if order.delivery_slot else None,
            'trackingUrl': None,
        }

        payment_data = {
            'method': _PAYMENT_LABELS.get(order.payment_method, order.payment_method),
            'trackingCode': order.payment_tracking_code or None,
            'amount': order.final_total,
            'paidAt': to_persian_date(order.paid_at) if order.paid_at else None,
        }

        return success_response({
            'id': order.id,
            'orderNumber': order.order_number,
            'date': to_persian_date(order.created_at),
            'status': status_int,
            'statusLabel': status_label,
            'items': items,
            'address': address_data,
            'payment': payment_data,
            'delivery': delivery_data,
        })
