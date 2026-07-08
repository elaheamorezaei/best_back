import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.responses import success_response, error_response
from .models import UserProfile, OTPCode, LoginAttempt, PasswordResetSession
from .serializers import (
    PhoneCheckSerializer, LoginPasswordSerializer,
    OTPSendSerializer, OTPVerifySerializer,
    ForgotPasswordSendOTPSerializer, ForgotPasswordVerifyOTPSerializer,
    ForgotPasswordResetSerializer, serialize_user,
    ProfileSerializer, ProfileUpdateSerializer, PasswordChangeSerializer,
)

User = get_user_model()

OTP_TTL = 120          # 2 minutes expiry
OTP_RESEND_COOLDOWN = 60   # minimum seconds between resends


def _token_response(user):
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    expires_in = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
    return {
        'accessToken': str(access),
        'refreshToken': str(refresh),
        'expiresIn': expires_in,
    }


def _validation_error(message, errors=None):
    body = {'success': False, 'message': message}
    if errors:
        body['errors'] = errors
    return Response(body, status=422)


def _auth_error(message, code=None, status=401):
    body = {'success': False, 'message': message}
    if code:
        body['code'] = code
    return Response(body, status=status)


# ---------------------------------------------------------------------------
# 1. POST /auth/phone/
# ---------------------------------------------------------------------------
class PhoneCheckView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PhoneCheckSerializer(data=request.data)
        if not serializer.is_valid():
            field = 'phoneNumber'
            msg = str(serializer.errors.get(field, ['شماره موبایل نامعتبر است'])[0])
            return _validation_error(msg, {field: msg})

        phone = serializer.validated_data['phoneNumber']
        is_registered = UserProfile.objects.filter(phone_number=phone).exists()

        return success_response({
            'isRegistered': is_registered,
            'nextStep': 'password' if is_registered else 'otp',
            'phoneNumber': phone,
            'maskedPhone': UserProfile.mask_phone(phone),
        })


# ---------------------------------------------------------------------------
# 2. POST /auth/login/password/
# ---------------------------------------------------------------------------
class LoginPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            field = next(iter(serializer.errors))
            msg = str(serializer.errors[field][0])
            return _validation_error(msg, {field: msg})

        phone = serializer.validated_data['phoneNumber']
        password = serializer.validated_data['password']

        attempt, _ = LoginAttempt.objects.get_or_create(phone_number=phone)
        if attempt.is_locked:
            return Response({
                'success': False,
                'message': f"تعداد تلاش‌های ناموفق بیش از حد مجاز است. {attempt.retry_after_seconds // 60} دقیقه دیگر تلاش کنید.",
                'data': {'retryAfterSeconds': attempt.retry_after_seconds},
            }, status=429)

        try:
            profile = UserProfile.objects.select_related('user').get(phone_number=phone)
        except UserProfile.DoesNotExist:
            return _auth_error("شماره موبایل یافت نشد", status=404)

        user = profile.user
        if not user.check_password(password):
            attempt.record_failure()
            return _auth_error("رمز عبور اشتباه است", code="INVALID_PASSWORD")

        attempt.reset()
        tokens = _token_response(user)
        return success_response({
            **tokens,
            'user': serialize_user(user, request),
        })


# ---------------------------------------------------------------------------
# 3. POST /auth/otp/send/
# ---------------------------------------------------------------------------
class OTPSendView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        if not serializer.is_valid():
            field = 'phoneNumber'
            msg = str(serializer.errors.get(field, ['شماره موبایل نامعتبر است'])[0])
            return _validation_error(msg, {field: msg})

        phone = serializer.validated_data['phoneNumber']

        seconds_ago = OTPCode.seconds_since_last(phone, OTPCode.PURPOSE_LOGIN)
        if seconds_ago is not None and seconds_ago < OTP_RESEND_COOLDOWN:
            wait = OTP_RESEND_COOLDOWN - seconds_ago
            return Response({
                'success': False,
                'message': f"هنوز {wait} ثانیه تا ارسال مجدد باقی است",
                'data': {'retryAfterSeconds': wait},
            }, status=429)

        otp = OTPCode.generate(phone, OTPCode.PURPOSE_LOGIN, ttl_seconds=OTP_TTL)

        data = {
            'maskedPhone': UserProfile.mask_phone(phone),
            'expiresInSeconds': OTP_TTL,
            'canResendAfterSeconds': OTP_RESEND_COOLDOWN,
        }
        if settings.DEBUG:
            data['debugCode'] = otp.code

        return Response({'success': True, 'message': 'کد تایید ارسال شد', 'data': data})


# ---------------------------------------------------------------------------
# 4. POST /auth/otp/verify/
# ---------------------------------------------------------------------------
class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if not serializer.is_valid():
            field = next(iter(serializer.errors))
            msg = str(serializer.errors[field][0])
            return _validation_error(msg, {field: msg})

        phone = serializer.validated_data['phoneNumber']
        code = serializer.validated_data['code']

        if not (settings.DEBUG and code == '12345'):
            otp = OTPCode.objects.filter(
                phone_number=phone, purpose=OTPCode.PURPOSE_LOGIN, is_used=False
            ).first()

            if not otp:
                return _auth_error("کد تایید اشتباه است", code="INVALID_OTP", status=422)

            if otp.is_expired:
                otp.is_used = True
                otp.save(update_fields=['is_used'])
                return _auth_error("کد تایید منقضی شده است. کد جدید دریافت کنید.", code="EXPIRED_OTP", status=410)

            if otp.code != code:
                return _auth_error("کد تایید اشتباه است", code="INVALID_OTP", status=422)

            otp.is_used = True
            otp.save(update_fields=['is_used'])

        try:
            profile = UserProfile.objects.select_related('user').get(phone_number=phone)
            user = profile.user
            is_new_user = False
        except UserProfile.DoesNotExist:
            user = User.objects.create_user(username=phone, password=None)
            user.set_unusable_password()
            user.save()
            profile = UserProfile.objects.create(user=user, phone_number=phone)
            is_new_user = True

        tokens = _token_response(user)
        return success_response({
            **tokens,
            'isNewUser': is_new_user,
            'user': serialize_user(user, request),
        })


# ---------------------------------------------------------------------------
# 5. POST /auth/forgot-password/send-otp/
# ---------------------------------------------------------------------------
class ForgotPasswordSendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            field = 'phoneNumber'
            msg = str(serializer.errors.get(field, ['شماره موبایل نامعتبر است'])[0])
            return _validation_error(msg, {field: msg})

        phone = serializer.validated_data['phoneNumber']

        if not UserProfile.objects.filter(phone_number=phone).exists():
            return error_response("شماره موبایل در سیستم ثبت نشده است", status=404)

        seconds_ago = OTPCode.seconds_since_last(phone, OTPCode.PURPOSE_FORGOT)
        if seconds_ago is not None and seconds_ago < OTP_RESEND_COOLDOWN:
            wait = OTP_RESEND_COOLDOWN - seconds_ago
            return Response({
                'success': False,
                'message': f"هنوز {wait} ثانیه تا ارسال مجدد باقی است",
                'data': {'retryAfterSeconds': wait},
            }, status=429)

        otp = OTPCode.generate(phone, OTPCode.PURPOSE_FORGOT, ttl_seconds=OTP_TTL)
        reset_token = uuid.uuid4().hex

        PasswordResetSession.objects.filter(phone_number=phone, is_used=False).update(is_used=True)
        PasswordResetSession.objects.create(
            phone_number=phone,
            reset_token=reset_token,
            expires_at=timezone.now() + timezone.timedelta(seconds=OTP_TTL),
        )

        data = {
            'maskedPhone': UserProfile.mask_phone(phone),
            'expiresInSeconds': OTP_TTL,
            'resetToken': reset_token,
        }
        if settings.DEBUG:
            data['debugCode'] = otp.code

        return Response({'success': True, 'message': 'کد تایید به شماره موبایل شما ارسال شد', 'data': data})


# ---------------------------------------------------------------------------
# 6. POST /auth/forgot-password/verify-otp/
# ---------------------------------------------------------------------------
class ForgotPasswordVerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordVerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            field = next(iter(serializer.errors))
            msg = str(serializer.errors[field][0])
            return _validation_error(msg, {field: msg})

        phone = serializer.validated_data['phoneNumber']
        code = serializer.validated_data['code']
        reset_token = serializer.validated_data['resetToken']

        try:
            session = PasswordResetSession.objects.get(
                phone_number=phone, reset_token=reset_token,
                step=PasswordResetSession.STEP_OTP_SENT, is_used=False,
            )
        except PasswordResetSession.DoesNotExist:
            return _auth_error("توکن بازنشانی نامعتبر است", code="INVALID_RESET_TOKEN", status=422)

        if session.is_expired:
            return _auth_error("توکن بازنشانی منقضی شده است. مجدد درخواست کنید.", code="EXPIRED_RESET_TOKEN", status=410)

        otp = OTPCode.objects.filter(
            phone_number=phone, purpose=OTPCode.PURPOSE_FORGOT, is_used=False
        ).first()

        if not otp or otp.is_expired or otp.code != code:
            code_str = "EXPIRED_OTP" if (otp and otp.is_expired) else "INVALID_OTP"
            msg = "کد تایید منقضی شده است" if (otp and otp.is_expired) else "کد تایید اشتباه است"
            return _auth_error(msg, code=code_str, status=422)

        otp.is_used = True
        otp.save(update_fields=['is_used'])

        change_token = uuid.uuid4().hex
        session.change_token = change_token
        session.step = PasswordResetSession.STEP_OTP_VERIFIED
        session.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        session.save()

        return success_response({'verified': True, 'changeToken': change_token})


# ---------------------------------------------------------------------------
# 7. POST /auth/forgot-password/reset/
# ---------------------------------------------------------------------------
class ForgotPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            errors = {}
            raw = serializer.errors
            if 'non_field_errors' in raw:
                nested = raw['non_field_errors']
                if isinstance(nested, list):
                    for item in nested:
                        if isinstance(item, dict):
                            errors.update(item)
            if isinstance(raw, dict):
                for k, v in raw.items():
                    if k != 'non_field_errors':
                        errors[k] = str(v[0]) if isinstance(v, list) else str(v)
            return _validation_error("خطای اعتبارسنجی", errors or raw)

        change_token = serializer.validated_data['changeToken']
        new_password = serializer.validated_data['newPassword']

        try:
            session = PasswordResetSession.objects.get(
                change_token=change_token,
                step=PasswordResetSession.STEP_OTP_VERIFIED,
                is_used=False,
            )
        except PasswordResetSession.DoesNotExist:
            return _auth_error("توکن تغییر رمز نامعتبر است", code="INVALID_CHANGE_TOKEN", status=422)

        if session.is_expired:
            return _auth_error("توکن تغییر رمز منقضی شده است. مجدد درخواست کنید.", code="EXPIRED_CHANGE_TOKEN", status=410)

        try:
            profile = UserProfile.objects.select_related('user').get(phone_number=session.phone_number)
        except UserProfile.DoesNotExist:
            return error_response("کاربر یافت نشد", status=404)

        user = profile.user
        user.set_password(new_password)
        user.save()

        session.is_used = True
        session.save(update_fields=['is_used'])

        tokens = _token_response(user)
        return Response({
            'success': True,
            'message': 'رمز عبور با موفقیت تغییر یافت',
            'data': {
                'accessToken': tokens['accessToken'],
                'refreshToken': tokens['refreshToken'],
            },
        })


# ---------------------------------------------------------------------------
# 8. POST /auth/logout/
# ---------------------------------------------------------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refreshToken', '')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except (TokenError, Exception):
                pass
        return Response({'success': True, 'message': 'با موفقیت خارج شدید'})


# ---------------------------------------------------------------------------
# 9. POST /auth/refresh/
# ---------------------------------------------------------------------------
class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refreshToken', '').strip()
        if not refresh_token:
            return error_response("refreshToken الزامی است", status=400)
        try:
            token = RefreshToken(refresh_token)
            access = token.access_token
            expires_in = int(settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
            return success_response({
                'accessToken': str(access),
                'expiresIn': expires_in,
            })
        except TokenError:
            return _auth_error("توکن نامعتبر یا منقضی است", code="INVALID_TOKEN", status=401)


# ---------------------------------------------------------------------------
# Profile views
# ---------------------------------------------------------------------------

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user, context={'request': request})
        return success_response(serializer.data)

    def put(self, request):
        serializer = ProfileUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            errors = {}
            for field, msgs in serializer.errors.items():
                if field == 'non_field_errors':
                    for item in msgs:
                        if isinstance(item, dict):
                            errors.update(item)
                else:
                    errors[field] = str(msgs[0]) if isinstance(msgs, list) else str(msgs)
            return Response({'success': False, 'message': 'خطای اعتبارسنجی', 'errors': errors}, status=422)

        data = serializer.validated_data
        user = request.user
        profile = getattr(user, 'profile', None)

        if 'email' in data:
            user.email = data['email']
            user.save(update_fields=['email'])

        if profile:
            update_fields = []
            if 'fullName' in data:
                profile.full_name = data['fullName']
                update_fields.append('full_name')
            if 'gender' in data:
                profile.gender = data['gender']
                update_fields.append('gender')
            if 'birthDate' in data:
                profile.birth_date = data['birthDate']
                update_fields.append('birth_date')
            if 'address' in data:
                profile.address = data['address']
                update_fields.append('address')
            if update_fields:
                profile.save(update_fields=update_fields)

        return Response({
            'success': True,
            'message': 'اطلاعات با موفقیت ذخیره شد',
            'data': {
                'id': user.id,
                'fullName': profile.full_name if profile else '',
                'gender': profile.gender if profile else '',
                'email': user.email or '',
                'birthDate': profile.birth_date if profile else '',
                'address': profile.address if profile else '',
            },
        })


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        avatar_file = request.FILES.get('avatar')
        if not avatar_file:
            return Response({'success': False, 'message': 'فایل آواتار الزامی است'}, status=400)

        if avatar_file.size > 2 * 1024 * 1024:
            return Response({'success': False, 'message': 'حجم فایل نباید بیشتر از ۲ مگابایت باشد'}, status=400)

        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return Response({'success': False, 'message': 'فرمت فایل باید JPG، PNG یا WEBP باشد'}, status=400)

        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'success': False, 'message': 'پروفایل یافت نشد'}, status=404)

        if profile.avatar:
            try:
                profile.avatar.delete(save=False)
            except Exception:
                pass

        profile.avatar = avatar_file
        profile.save(update_fields=['avatar'])

        from core.responses import build_absolute_image_url
        avatar_url = build_absolute_image_url(request, profile.avatar)
        return success_response({'avatarUrl': avatar_url}, status=200)


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if not serializer.is_valid():
            errors = {}
            raw = serializer.errors
            if 'non_field_errors' in raw:
                for item in raw['non_field_errors']:
                    if isinstance(item, dict):
                        errors.update(item)
            for field, msgs in raw.items():
                if field != 'non_field_errors':
                    errors[field] = str(msgs[0]) if isinstance(msgs, list) else str(msgs)
            return Response({
                'success': False, 'message': 'خطای اعتبارسنجی', 'errors': errors
            }, status=422)

        data = serializer.validated_data
        user = request.user

        if not user.check_password(data['currentPassword']):
            return Response({
                'success': False,
                'message': 'رمز عبور فعلی اشتباه است',
                'code': 'WRONG_CURRENT_PASSWORD',
            }, status=401)

        user.set_password(data['newPassword'])
        user.save()
        return Response({'success': True, 'message': 'رمز عبور با موفقیت تغییر یافت'})
