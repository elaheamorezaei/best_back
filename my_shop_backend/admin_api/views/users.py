import uuid
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response

from admin_api.permissions import IsAdminUser
from users.models import UserProfile
from core.responses import build_absolute_image_url

User = get_user_model()


def _serialize_user(user, request=None):
    profile = getattr(user, 'profile', None)
    wallet = getattr(user, 'wallet', None)
    orders_agg = user.orders.aggregate(count=Count('id'), total=Sum('final_total'))
    avatar = build_absolute_image_url(request, profile.avatar) if profile and profile.avatar else None
    return {
        'id': user.id,
        'fullName': profile.full_name if profile else user.get_full_name(),
        'email': user.email,
        'phone': profile.phone_number if profile else '',
        'avatar': avatar,
        'isActive': user.is_active,
        'ordersCount': orders_agg['count'] or 0,
        'totalSpent': orders_agg['total'] or 0,
        'walletBalance': wallet.balance if wallet else 0,
        'joinedAt': user.date_joined.isoformat(),
        'lastLogin': user.last_login.isoformat() if user.last_login else None,
    }


class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = User.objects.select_related('profile', 'wallet').prefetch_related('orders')

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(profile__phone_number__icontains=search) | qs.filter(profile__full_name__icontains=search) | qs.filter(email__icontains=search)

        if request.query_params.get('isActive') == 'true':
            qs = qs.filter(is_active=True)
        elif request.query_params.get('isActive') == 'false':
            qs = qs.filter(is_active=False)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = max(1, min(100, int(request.query_params.get('pageSize', 20))))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        total = qs.count()
        start = (page - 1) * page_size
        items = list(qs[start:start + page_size])

        return Response({
            'results': [_serialize_user(u, request) for u in items],
            'count': total,
            'next': None,
            'previous': None,
        })


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            user = User.objects.select_related('profile', 'wallet').prefetch_related('orders').get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': {'message': 'کاربر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        return Response(_serialize_user(user, request))

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': {'message': 'کاربر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        if user == request.user:
            return Response({'error': {'message': 'نمی‌توانید حساب خود را حذف کنید', 'code': 'SELF_DELETE'}}, status=400)
        user.delete()
        return Response(status=204)


class AdminUserToggleActiveView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': {'message': 'کاربر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return Response({'isActive': user.is_active})


class AdminUserWalletView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': {'message': 'کاربر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        amount = request.data.get('amount')
        description = request.data.get('description', '')

        if amount is None:
            return Response({'error': {'message': 'مبلغ الزامی است', 'code': 'MISSING_AMOUNT'}}, status=400)

        try:
            amount = int(amount)
        except (ValueError, TypeError):
            return Response({'error': {'message': 'مبلغ نامعتبر است', 'code': 'INVALID_AMOUNT'}}, status=400)

        from wallet.models import Wallet, WalletTransaction
        wallet, _ = Wallet.objects.get_or_create(user=user, defaults={'balance': 0, 'is_active': True})
        wallet.balance += amount
        wallet.save(update_fields=['balance'])

        tx_type = WalletTransaction.TYPE_DEPOSIT if amount > 0 else WalletTransaction.TYPE_WITHDRAW
        tx = WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            type=tx_type,
            tracking_code=WalletTransaction.generate_tracking_code('ADM'),
            description=description,
        )

        return Response({
            'walletBalance': wallet.balance,
            'transaction': {
                'id': tx.id,
                'amount': tx.amount,
                'description': tx.description,
                'createdAt': tx.created_at.isoformat(),
            },
        })
