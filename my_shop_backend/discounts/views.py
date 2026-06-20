import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.responses import success_response, error_response
from .models import DiscountCode, GiftCard


class DiscountCodeValidateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code', '').strip()
        cart_total = request.data.get('cart_total', 0)
        if not code:
            return error_response("کد تخفیف الزامی است", status=400)
        try:
            cart_total = int(cart_total)
        except (ValueError, TypeError):
            return error_response("مبلغ سبد خرید نامعتبر است", status=400)

        try:
            discount = DiscountCode.objects.get(code=code, is_active=True)
        except DiscountCode.DoesNotExist:
            return error_response("کد تخفیف معتبر نیست", status=404)

        if discount.expires_at and discount.expires_at < datetime.date.today():
            return error_response("کد تخفیف منقضی شده است", status=400)
        if discount.usage_limit and discount.used_count >= discount.usage_limit:
            return error_response("ظرفیت استفاده از این کد تکمیل شده است", status=400)
        if cart_total < discount.min_cart_total:
            return error_response(
                f"حداقل مبلغ سبد خرید برای این کد {discount.min_cart_total:,} تومان است",
                status=400,
            )

        discount_amount = discount.calc_discount(cart_total)
        return success_response({
            'code': discount.code,
            'discountType': discount.discount_type,
            'discountValue': discount.discount_value,
            'maxDiscount': discount.max_discount,
            'discountAmount': discount_amount,
        })


class GiftCardValidateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code', '').strip()
        if not code:
            return error_response("کد کارت هدیه الزامی است", status=400)

        try:
            gift_card = GiftCard.objects.get(code=code, is_active=True)
        except GiftCard.DoesNotExist:
            return error_response("کارت هدیه معتبر نیست", status=404)

        if gift_card.expires_at and gift_card.expires_at < datetime.date.today():
            return error_response("کارت هدیه منقضی شده است", status=400)

        return success_response({
            'code': gift_card.code,
            'balance': gift_card.balance,
        })
