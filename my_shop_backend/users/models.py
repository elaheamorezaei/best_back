import random
from django.db import models
from django.conf import settings
from django.utils import timezone


class UserProfile(models.Model):
    GENDER_MALE = 'آقا'
    GENDER_FEMALE = 'خانم'
    GENDER_CHOICES = [(GENDER_MALE, 'Male'), (GENDER_FEMALE, 'Female')]

    ROLE_SUPERADMIN = 'superadmin'
    ROLE_ADMIN = 'admin'
    ROLE_EDITOR = 'editor'
    ROLE_SUPPORT = 'support'
    ROLE_CHOICES = [
        (ROLE_SUPERADMIN, 'Super Admin'),
        (ROLE_ADMIN, 'Admin'),
        (ROLE_EDITOR, 'Editor'),
        (ROLE_SUPPORT, 'Support'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE
    )
    phone_number = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(upload_to='users/avatars/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    birth_date = models.CharField(max_length=10, blank=True)
    national_code = models.CharField(max_length=10, blank=True)
    address = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)

    def __str__(self):
        return f"{self.phone_number} — {self.user.username}"

    @staticmethod
    def mask_phone(phone):
        if len(phone) >= 7:
            return phone[:4] + '***' + phone[7:]
        return phone


class OTPCode(models.Model):
    PURPOSE_LOGIN = 'login'
    PURPOSE_FORGOT = 'forgot_password'
    PURPOSE_WALLET = 'wallet_activate'
    PURPOSE_CHOICES = [
        (PURPOSE_LOGIN, 'Login / Register'),
        (PURPOSE_FORGOT, 'Forgot Password'),
        (PURPOSE_WALLET, 'Wallet Activation'),
    ]

    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default=PURPOSE_LOGIN)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone_number} [{self.purpose}]"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def generate(cls, phone_number, purpose=PURPOSE_LOGIN, ttl_seconds=120):
        cls.objects.filter(
            phone_number=phone_number, purpose=purpose, is_used=False
        ).update(is_used=True)
        code = '1234' if settings.DEBUG else str(random.randint(1000, 9999))
        return cls.objects.create(
            phone_number=phone_number,
            code=code,
            purpose=purpose,
            expires_at=timezone.now() + timezone.timedelta(seconds=ttl_seconds),
        )

    @classmethod
    def seconds_since_last(cls, phone_number, purpose=PURPOSE_LOGIN):
        last = cls.objects.filter(phone_number=phone_number, purpose=purpose).first()
        if not last:
            return None
        return int((timezone.now() - last.created_at).total_seconds())


class LoginAttempt(models.Model):
    MAX_ATTEMPTS = 5
    LOCKOUT_SECONDS = 900

    phone_number = models.CharField(max_length=15, unique=True)
    attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_attempt_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} — {self.attempts} attempts"

    @property
    def is_locked(self):
        return bool(self.locked_until and timezone.now() < self.locked_until)

    @property
    def retry_after_seconds(self):
        if self.locked_until:
            return max(0, int((self.locked_until - timezone.now()).total_seconds()))
        return 0

    def record_failure(self):
        self.attempts += 1
        if self.attempts >= self.MAX_ATTEMPTS:
            self.locked_until = timezone.now() + timezone.timedelta(seconds=self.LOCKOUT_SECONDS)
        self.save()

    def reset(self):
        self.attempts = 0
        self.locked_until = None
        self.save()


class PasswordResetSession(models.Model):
    STEP_OTP_SENT = 1
    STEP_OTP_VERIFIED = 2

    phone_number = models.CharField(max_length=15)
    reset_token = models.CharField(max_length=64, unique=True)
    change_token = models.CharField(max_length=64, blank=True)
    step = models.PositiveSmallIntegerField(default=STEP_OTP_SENT)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone_number} step={self.step}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
