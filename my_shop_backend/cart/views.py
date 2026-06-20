from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.responses import success_response, error_response
from .models import CartItem, InsurancePlan
from .serializers import CartItemSerializer, InsurancePlanSerializer
from products.models import Product, ProductColor, ProductWarranty


def _cart_summary(user, request):
    items = CartItem.objects.filter(
        user=user, list_type=CartItem.LIST_CURRENT
    ).select_related('product', 'color', 'guarantee', 'insurance').prefetch_related('product__images')

    next_items = CartItem.objects.filter(
        user=user, list_type=CartItem.LIST_NEXT
    ).select_related('product', 'color', 'guarantee', 'insurance').prefetch_related('product__images')

    serializer = CartItemSerializer(items, many=True, context={'request': request})
    next_serializer = CartItemSerializer(next_items, many=True, context={'request': request})

    products_total = sum(
        item.product.final_price * item.quantity for item in items
    )
    insurance_total = sum(
        (item.insurance.price if item.insurance else 0) * item.quantity for item in items
    )

    return {
        'items': serializer.data,
        'nextItems': next_serializer.data,
        'summary': {
            'productsTotal': products_total,
            'insuranceTotal': insurance_total,
            'total': products_total + insurance_total,
            'itemCount': sum(item.quantity for item in items),
        },
    }


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(_cart_summary(request.user, request))

    def post(self, request):
        product_id = request.data.get('productId')
        color_id = request.data.get('colorId')
        guarantee_id = request.data.get('guaranteeId')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return error_response("شناسه محصول الزامی است", status=400)
        try:
            quantity = max(1, int(quantity))
        except (ValueError, TypeError):
            quantity = 1

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return error_response("محصول یافت نشد", status=404)

        if not product.in_stock:
            return error_response("محصول موجود نیست", status=400)

        color = None
        if color_id:
            try:
                color = ProductColor.objects.get(pk=color_id, product=product)
            except ProductColor.DoesNotExist:
                return error_response("رنگ انتخابی یافت نشد", status=404)

        guarantee = None
        if guarantee_id:
            try:
                guarantee = ProductWarranty.objects.get(pk=guarantee_id, product=product)
            except ProductWarranty.DoesNotExist:
                return error_response("گارانتی انتخابی یافت نشد", status=404)

        item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            color=color,
            guarantee=guarantee,
            list_type=CartItem.LIST_CURRENT,
            defaults={'quantity': quantity},
        )
        if not created:
            item.quantity += quantity
            item.save()

        return success_response(_cart_summary(request.user, request), status=201)


class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_item(self, request, item_id):
        try:
            return CartItem.objects.get(pk=item_id, user=request.user)
        except CartItem.DoesNotExist:
            return None

    def put(self, request, item_id):
        item = self._get_item(request, item_id)
        if not item:
            return error_response("آیتم سبد خرید یافت نشد", status=404)
        quantity = request.data.get('quantity')
        if quantity is not None:
            try:
                quantity = int(quantity)
            except (ValueError, TypeError):
                return error_response("مقدار نامعتبر است", status=400)
            if quantity < 1:
                item.delete()
                return success_response(_cart_summary(request.user, request))
            item.quantity = quantity
            item.save()
        return success_response(_cart_summary(request.user, request))

    def delete(self, request, item_id):
        item = self._get_item(request, item_id)
        if not item:
            return error_response("آیتم سبد خرید یافت نشد", status=404)
        item.delete()
        return success_response(_cart_summary(request.user, request))


class CartItemMoveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        try:
            item = CartItem.objects.get(pk=item_id, user=request.user)
        except CartItem.DoesNotExist:
            return error_response("آیتم سبد خرید یافت نشد", status=404)

        target = request.data.get('target')
        if target not in (CartItem.LIST_CURRENT, CartItem.LIST_NEXT):
            return error_response("مقصد نامعتبر است. مقادیر مجاز: current, next", status=400)
        item.list_type = target
        item.save()
        return success_response(_cart_summary(request.user, request))


class CartItemInsuranceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        try:
            item = CartItem.objects.get(pk=item_id, user=request.user)
        except CartItem.DoesNotExist:
            return error_response("آیتم سبد خرید یافت نشد", status=404)

        insurance_id = request.data.get('insuranceId')
        if insurance_id is None:
            item.insurance = None
            item.save()
            return success_response(_cart_summary(request.user, request))
        try:
            plan = InsurancePlan.objects.get(pk=insurance_id, is_active=True)
        except InsurancePlan.DoesNotExist:
            return error_response("پلن بیمه یافت نشد", status=404)
        item.insurance = plan
        item.save()
        return success_response(_cart_summary(request.user, request))


class InsurancePlansView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plans = InsurancePlan.objects.filter(is_active=True)
        serializer = InsurancePlanSerializer(plans, many=True)
        return success_response(serializer.data)
