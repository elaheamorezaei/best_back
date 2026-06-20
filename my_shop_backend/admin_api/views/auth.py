from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()


def _admin_token_response(user):
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    profile = getattr(user, 'profile', None)
    role = profile.role if profile and profile.role else ('superadmin' if user.is_superuser else 'admin')
    access['role'] = role
    refresh['role'] = role
    return {
        'access': str(access),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': role,
            'fullName': profile.full_name if profile else user.get_full_name(),
            'avatar': None,
            'isActive': user.is_active,
            'lastLogin': user.last_login.isoformat() if user.last_login else None,
            'createdAt': user.date_joined.isoformat(),
        },
    }


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')

        if not email or not password:
            return Response({'error': {'message': 'ایمیل و رمز عبور الزامی است', 'code': 'MISSING_CREDENTIALS'}}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': {'message': 'کاربر یافت نشد', 'code': 'USER_NOT_FOUND'}}, status=401)

        if not user.check_password(password):
            return Response({'error': {'message': 'رمز عبور اشتباه است', 'code': 'INVALID_PASSWORD'}}, status=401)

        if not user.is_staff:
            return Response({'error': {'message': 'دسترسی ادمین ندارید', 'code': 'NOT_ADMIN'}}, status=403)

        if not user.is_active:
            return Response({'error': {'message': 'حساب غیرفعال است', 'code': 'INACTIVE'}}, status=401)

        return Response(_admin_token_response(user), status=200)


class AdminTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh', '').strip()
        if not refresh_token:
            return Response({'error': {'message': 'refresh token الزامی است', 'code': 'MISSING_TOKEN'}}, status=400)
        try:
            token = RefreshToken(refresh_token)
            return Response({'access': str(token.access_token)}, status=200)
        except TokenError:
            return Response({'error': {'message': 'توکن نامعتبر است', 'code': 'INVALID_TOKEN'}}, status=401)


class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh', '').strip()
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except (TokenError, Exception):
                pass
        return Response(status=204)
