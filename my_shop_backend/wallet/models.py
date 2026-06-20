import uuid as uuid_lib
from django.db import models
from django.conf import settings
from django.utils import timezone


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='wallet', on_delete=models.CASCADE
    )
    balance = models.BigIntegerField(default=0)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} — {self.balance} تومان"


class WalletTransaction(models.Model):
    TYPE_DEPOSIT = 'deposit'
    TYPE_WITHDRAW = 'withdraw'
    TYPE_PURCHASE = 'purchase'
    TYPE_CHOICES = [
        (TYPE_DEPOSIT, 'واریز'),
        (TYPE_WITHDRAW, 'برداشت'),
        (TYPE_PURCHASE, 'خرید'),
    ]

    STATUS_SUCCESS = 1   # کامل
    STATUS_WITHDRAW = 2  # برداشت
    STATUS_CHARGE = 3    # شارژ / در صف بررسی
    STATUS_SPENT = 4     # مصرف‌شده
    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'کامل'),
        (STATUS_WITHDRAW, 'برداشت'),
        (STATUS_CHARGE, 'شارژ'),
        (STATUS_SPENT, 'مصرف‌شده'),
    ]
    STATUS_LABELS = {
        STATUS_SUCCESS: 'کامل',
        STATUS_WITHDRAW: 'برداشت',
        STATUS_CHARGE: 'شارژ',
        STATUS_SPENT: 'مصرف‌شده',
    }

    wallet = models.ForeignKey(Wallet, related_name='transactions', on_delete=models.CASCADE)
    # Positive = credit (deposit), negative = debit (withdraw/purchase)
    amount = models.BigIntegerField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=STATUS_SUCCESS)
    tracking_code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.wallet.user} — {self.amount}"

    @classmethod
    def generate_tracking_code(cls, prefix='TRX'):
        return f"{prefix}-{uuid_lib.uuid4().hex[:8].upper()}"


class WalletIncreaseRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    wallet = models.ForeignKey(Wallet, related_name='increase_requests', on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    token = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=10, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.wallet.user} — {self.amount} [{self.status}]"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
