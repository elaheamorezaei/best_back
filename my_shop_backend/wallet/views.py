import math
import uuid
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.responses import success_response, error_response
from core.utils import to_persian_date
from users.models import OTPCode, UserProfile
from .models import Wallet, WalletTransaction, WalletIncreaseRequest


OTP_TTL = 120
OTP_RESEND_COOLDOWN = 60

# Limits (Tomans)
INCREASE_MIN = 100_000
INCREASE_MAX = 200_000_000
WITHDRAW_MIN = 50_000
WITHDRAW_MAX = 50_000_000
# Withdraw amounts above this go to review queue
WITHDRAW_REVIEW_THRESHOLD = 1_000_000


def _get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


def _format_amount(amount):
    """'+500000' or '-200000'"""
    return f"+{amount}" if amount >= 0 else str(amount)


def _format_amount_label(amount):
    """'+ 500,000 تومان' or '- 200,000 تومان'"""
    sign = '+' if amount >= 0 else '-'
    return f"{sign} {abs(amount):,} تومان"


def _serialize_transaction(tx, row=None):
    data = {
        'id': tx.id,
        'date': to_persian_date(tx.created_at),
        'trackingCode': tx.tracking_code,
        'amount': _format_amount(tx.amount),
        'amountLabel': _format_amount_label(tx.amount),
        'status': tx.status,
        'statusLabel': WalletTransaction.STATUS_LABELS.get(tx.status, ''),
        'type': tx.type,
        'description': tx.description,
    }
    if row is not None:
        data['row'] = row
    return data


def _jalali_to_date(jalali_str):
    try:
        import jdatetime, datetime
        y, m, d = map(int, jalali_str.split('/'))
        g = jdatetime.date(y, m, d).togregorian()
        return timezone.make_aware(datetime.datetime.combine(g, datetime.time.min))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# GET /wallet
# ---------------------------------------------------------------------------
class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = _get_or_create_wallet(request.user)
        recent_txs = list(wallet.transactions.all()[:5])

        transactions = [
            _serialize_transaction(tx, row=i + 1)
            for i, tx in enumerate(recent_txs)
        ]
        total_count = wallet.transactions.count()

        return success_response({
            'balance': wallet.balance,
            'isActive': wallet.is_active,
            'transactions': transactions,
            'pagination': {'page': 1, 'total': total_count},
        })


# ---------------------------------------------------------------------------
# POST /wallet/activate/send-otp
# ---------------------------------------------------------------------------
class WalletActivateSendOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet = _get_or_create_wallet(request.user)
        if wallet.is_active:
            return Response({'success': False, 'message': 'کیف پول قبلاً فعال شده است'}, status=400)

        profile = getattr(request.user, 'profile', None)
        if not profile:
            return error_response("پروفایل یافت نشد", status=404)

        phone = profile.phone_number
        seconds_ago = OTPCode.seconds_since_last(phone, OTPCode.PURPOSE_WALLET)
        if seconds_ago is not None and seconds_ago < OTP_RESEND_COOLDOWN:
            wait = OTP_RESEND_COOLDOWN - seconds_ago
            return Response({
                'success': False,
                'message': f"هنوز {wait} ثانیه تا ارسال مجدد باقی است",
                'data': {'retryAfterSeconds': wait},
            }, status=429)

        otp = OTPCode.generate(phone, OTPCode.PURPOSE_WALLET, ttl_seconds=OTP_TTL)
        data = {
            'maskedPhone': UserProfile.mask_phone(phone),
            'expiresInSeconds': OTP_TTL,
        }
        from django.conf import settings
        if settings.DEBUG:
            data['debugCode'] = otp.code

        return Response({'success': True, 'message': 'کد تایید ارسال شد', 'data': data})


# ---------------------------------------------------------------------------
# POST /wallet/activate/verify-otp
# ---------------------------------------------------------------------------
class WalletActivateVerifyOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code', '').strip()
        if not code:
            return Response({'success': False, 'data': {'status': 2, 'message': 'کد الزامی است'}}, status=400)

        profile = getattr(request.user, 'profile', None)
        if not profile:
            return error_response("پروفایل یافت نشد", status=404)

        phone = profile.phone_number
        otp = OTPCode.objects.filter(
            phone_number=phone, purpose=OTPCode.PURPOSE_WALLET, is_used=False
        ).first()

        if not otp:
            return Response({
                'success': False,
                'data': {'status': 2, 'message': 'کد وارد شده صحیح نمی‌باشد'},
            }, status=422)

        if otp.is_expired:
            otp.is_used = True
            otp.save(update_fields=['is_used'])
            return Response({
                'success': False,
                'data': {'status': 3, 'message': 'مدت اعتبار این کد به پایان رسیده است'},
            }, status=410)

        if otp.code != code:
            return Response({
                'success': False,
                'data': {'status': 2, 'message': 'کد وارد شده صحیح نمی‌باشد'},
            }, status=422)

        otp.is_used = True
        otp.save(update_fields=['is_used'])

        wallet = _get_or_create_wallet(request.user)
        wallet.is_active = True
        wallet.save(update_fields=['is_active'])

        return Response({'success': True, 'data': {'status': 1, 'message': 'کیف پول شما فعال شد.'}})


# ---------------------------------------------------------------------------
# POST /wallet/increase
# ---------------------------------------------------------------------------
class WalletIncreaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet = _get_or_create_wallet(request.user)
        if not wallet.is_active:
            return Response({'success': False, 'message': 'کیف پول شما فعال نیست'}, status=403)

        try:
            amount = int(request.data.get('amount', 0))
        except (ValueError, TypeError):
            return Response({'success': False, 'message': 'مبلغ نامعتبر است'}, status=400)

        if amount < INCREASE_MIN or amount > INCREASE_MAX:
            return Response({
                'success': False,
                'message': f"مبلغ باید بین {INCREASE_MIN:,} و {INCREASE_MAX:,} تومان باشد",
            }, status=400)

        token = uuid.uuid4().hex
        expires_at = timezone.now() + timezone.timedelta(minutes=30)
        WalletIncreaseRequest.objects.create(
            wallet=wallet, amount=amount, token=token, expires_at=expires_at
        )

        return success_response({
            'paymentUrl': f"/api/v1/payment/wallet/gateway/?token={token}",
            'token': token,
            'amount': amount,
            'expiresAt': expires_at.isoformat(),
        })


# ---------------------------------------------------------------------------
# POST /wallet/increase/verify
# ---------------------------------------------------------------------------
class WalletIncreaseVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.data.get('token', '').strip()
        status_param = request.data.get('status', '').strip()
        bank_code = request.data.get('bankTrackingCode', '').strip()

        if not token:
            return Response({'success': False, 'message': 'توکن الزامی است'}, status=400)

        wallet = _get_or_create_wallet(request.user)
        try:
            increase_req = WalletIncreaseRequest.objects.get(
                token=token, wallet=wallet, status=WalletIncreaseRequest.STATUS_PENDING
            )
        except WalletIncreaseRequest.DoesNotExist:
            return error_response("درخواست یافت نشد یا قبلاً پردازش شده است", status=404)

        if increase_req.is_expired:
            increase_req.status = WalletIncreaseRequest.STATUS_FAILED
            increase_req.save(update_fields=['status'])
            return Response({'success': False, 'message': 'مهلت پرداخت منقضی شده است'}, status=410)

        if status_param != 'success':
            increase_req.status = WalletIncreaseRequest.STATUS_FAILED
            increase_req.save(update_fields=['status'])
            return Response({'success': False, 'message': 'پرداخت ناموفق بود'}, status=400)

        amount = increase_req.amount
        tracking_code = WalletTransaction.generate_tracking_code('TRX')
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            type=WalletTransaction.TYPE_DEPOSIT,
            status=WalletTransaction.STATUS_SUCCESS,
            tracking_code=tracking_code,
            description='افزایش موجودی از طریق درگاه',
        )
        wallet.balance += amount
        wallet.save(update_fields=['balance'])

        increase_req.status = WalletIncreaseRequest.STATUS_SUCCESS
        increase_req.save(update_fields=['status'])

        return success_response({
            'newBalance': wallet.balance,
            'addedAmount': amount,
            'trackingCode': tracking_code,
        })


# ---------------------------------------------------------------------------
# POST /wallet/withdraw
# ---------------------------------------------------------------------------
class WalletWithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet = _get_or_create_wallet(request.user)
        if not wallet.is_active:
            return Response({'success': False, 'message': 'کیف پول شما فعال نیست'}, status=403)

        try:
            amount = int(request.data.get('amount', 0))
        except (ValueError, TypeError):
            return Response({'success': False, 'message': 'مبلغ نامعتبر است'}, status=400)

        if amount < WITHDRAW_MIN or amount > WITHDRAW_MAX:
            return Response({
                'success': False,
                'message': f"مبلغ باید بین {WITHDRAW_MIN:,} و {WITHDRAW_MAX:,} تومان باشد",
            }, status=400)

        if wallet.balance < amount:
            return Response({
                'success': False,
                'message': 'موجودی کافی نیست',
                'data': {'currentBalance': wallet.balance, 'requestedAmount': amount},
            }, status=422)

        tracking_code = WalletTransaction.generate_tracking_code('WDR')

        if amount <= WITHDRAW_REVIEW_THRESHOLD:
            wallet.balance -= amount
            wallet.save(update_fields=['balance'])
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=-amount,
                type=WalletTransaction.TYPE_WITHDRAW,
                status=WalletTransaction.STATUS_SUCCESS,
                tracking_code=tracking_code,
                description='برداشت وجه',
            )
            return success_response({
                'status': 1,
                'message': 'برداشت با موفقیت انجام شد.',
                'newBalance': wallet.balance,
                'trackingCode': tracking_code,
            })
        else:
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=-amount,
                type=WalletTransaction.TYPE_WITHDRAW,
                status=WalletTransaction.STATUS_CHARGE,
                tracking_code=tracking_code,
                description='درخواست برداشت در صف بررسی',
            )
            return success_response({
                'status': 3,
                'message': 'درخواست برداشت شما در صف بررسی است و به زودی انجام می‌شود.',
                'requestId': tracking_code,
            })


# ---------------------------------------------------------------------------
# GET /wallet/transactions
# ---------------------------------------------------------------------------
class WalletTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = _get_or_create_wallet(request.user)
        qs = wallet.transactions.all()

        tx_type = request.query_params.get('type', '').strip()
        if tx_type in (WalletTransaction.TYPE_DEPOSIT, WalletTransaction.TYPE_WITHDRAW,
                       WalletTransaction.TYPE_PURCHASE):
            qs = qs.filter(type=tx_type)

        from_date = request.query_params.get('fromDate', '').strip()
        if from_date:
            dt = _jalali_to_date(from_date)
            if dt:
                qs = qs.filter(created_at__gte=dt)

        to_date = request.query_params.get('toDate', '').strip()
        if to_date:
            dt = _jalali_to_date(to_date)
            if dt:
                import datetime
                end = timezone.make_aware(datetime.datetime.combine(dt.date(), datetime.time.max))
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
        total_pages = math.ceil(total / limit) if total else 1
        items = list(qs[(page - 1) * limit: page * limit])

        transactions = []
        for row_idx, tx in enumerate(items, start=(page - 1) * limit + 1):
            tx_data = _serialize_transaction(tx, row=row_idx)
            tx_data['amountFormatted'] = tx_data.pop('amountLabel')
            transactions.append(tx_data)

        return success_response({
            'transactions': transactions,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'totalPages': total_pages,
            },
        })
