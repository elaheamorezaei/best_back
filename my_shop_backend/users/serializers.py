import re
from rest_framework import serializers
from core.responses import build_absolute_image_url
from core.utils import to_persian_date


PHONE_RE = re.compile(r'^09\d{9}$')
PASSWORD_RE_UPPER = re.compile(r'[A-Z]')
PASSWORD_RE_LOWER = re.compile(r'[a-z]')
PASSWORD_RE_DIGIT = re.compile(r'[0-9]')


def validate_phone(phone):
    if not phone or not PHONE_RE.match(phone):
        raise serializers.ValidationError("شماره موبایل باید ۱۱ رقم و با ۰۹ شروع شود")
    return phone


def validate_password_strength(password):
    errors = []
    if len(password) < 8:
        errors.append("رمز عبور باید حداقل ۸ کاراکتر باشد")
    if not PASSWORD_RE_UPPER.search(password):
        errors.append("رمز عبور باید شامل حرف بزرگ باشد")
    if not PASSWORD_RE_LOWER.search(password):
        errors.append("رمز عبور باید شامل حرف کوچک باشد")
    if not PASSWORD_RE_DIGIT.search(password):
        errors.append("رمز عبور باید شامل عدد باشد")
    if errors:
        raise serializers.ValidationError(errors[0])
    return password


def serialize_user(user, request=None):
    profile = getattr(user, 'profile', None)
    avatar = None
    if profile and profile.avatar:
        avatar = build_absolute_image_url(request, profile.avatar)
    return {
        'id': user.id,
        'phoneNumber': profile.phone_number if profile else '',
        'fullName': profile.full_name if profile else user.get_full_name(),
        'email': user.email or '',
        'avatar': avatar,
    }


class PhoneCheckSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()

    def validate_phoneNumber(self, value):
        return validate_phone(value.strip())


class LoginPasswordSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()
    password = serializers.CharField()

    def validate_phoneNumber(self, value):
        return validate_phone(value.strip())


class OTPSendSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()

    def validate_phoneNumber(self, value):
        return validate_phone(value.strip())


class OTPVerifySerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()
    code = serializers.CharField(min_length=4, max_length=6)

    def validate_phoneNumber(self, value):
        return validate_phone(value.strip())


class ForgotPasswordSendOTPSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()

    def validate_phoneNumber(self, value):
        return validate_phone(value.strip())


class ForgotPasswordVerifyOTPSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField()
    code = serializers.CharField(min_length=4, max_length=6)
    resetToken = serializers.CharField()

    def validate_phoneNumber(self, value):
        return validate_phone(value.strip())


class ForgotPasswordResetSerializer(serializers.Serializer):
    changeToken = serializers.CharField()
    newPassword = serializers.CharField()
    confirmPassword = serializers.CharField()

    def validate(self, data):
        errors = {}
        try:
            validate_password_strength(data.get('newPassword', ''))
        except serializers.ValidationError as e:
            errors['newPassword'] = str(e.detail[0] if isinstance(e.detail, list) else e.detail)
        if data.get('newPassword') != data.get('confirmPassword'):
            errors['confirmPassword'] = "رمز عبور و تکرار آن یکسان نیستند"
        if errors:
            raise serializers.ValidationError(errors)
        return data


# ---------------------------------------------------------------------------
# Profile serializers
# ---------------------------------------------------------------------------

class ProfileSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    fullName = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    birthDate = serializers.SerializerMethodField()
    nationalCode = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()

    def get_id(self, user):
        return user.id

    def get_fullName(self, user):
        profile = getattr(user, 'profile', None)
        return profile.full_name if profile else ''

    def get_gender(self, user):
        profile = getattr(user, 'profile', None)
        return profile.gender if profile else ''

    def get_email(self, user):
        return user.email or ''

    def get_phone(self, user):
        profile = getattr(user, 'profile', None)
        return profile.phone_number if profile else ''

    def get_birthDate(self, user):
        profile = getattr(user, 'profile', None)
        return profile.birth_date if profile else ''

    def get_nationalCode(self, user):
        profile = getattr(user, 'profile', None)
        return profile.national_code if profile else ''

    def get_address(self, user):
        profile = getattr(user, 'profile', None)
        return profile.address if profile else ''

    def get_avatar(self, user):
        request = self.context.get('request')
        profile = getattr(user, 'profile', None)
        return build_absolute_image_url(request, profile.avatar) if profile else None

    def get_createdAt(self, user):
        return to_persian_date(user.date_joined)


class ProfileUpdateSerializer(serializers.Serializer):
    fullName = serializers.CharField(max_length=200, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(
        choices=['آقا', 'خانم', ''], required=False, allow_blank=True
    )
    birthDate = serializers.CharField(max_length=10, required=False, allow_blank=True)
    address = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_birthDate(self, value):
        if value and not re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', value):
            raise serializers.ValidationError("فرمت تاریخ تولد باید YYYY/MM/DD باشد")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    currentPassword = serializers.CharField()
    newPassword = serializers.CharField()
    confirmPassword = serializers.CharField()

    def validate(self, data):
        errors = {}
        try:
            validate_password_strength(data.get('newPassword', ''))
        except serializers.ValidationError as e:
            errors['newPassword'] = str(e.detail[0] if isinstance(e.detail, list) else e.detail)
        if data.get('newPassword') != data.get('confirmPassword'):
            errors['confirmPassword'] = "رمز عبور و تکرار آن یکسان نیستند"
        if errors:
            raise serializers.ValidationError(errors)
        return data
