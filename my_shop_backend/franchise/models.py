from django.db import models


class FranchiseApplication(models.Model):
    FRANCHISE_TYPE_STORE = 'store'
    FRANCHISE_TYPE_ONLINE = 'online'
    FRANCHISE_TYPE_HYBRID = 'hybrid'

    FRANCHISE_TYPE_CHOICES = [
        (FRANCHISE_TYPE_STORE, 'فروشگاهی (حضوری)'),
        (FRANCHISE_TYPE_ONLINE, 'اینترنتی (آنلاین)'),
        (FRANCHISE_TYPE_HYBRID, 'ترکیبی (حضوری + آنلاین)'),
    ]

    INVESTMENT_UNDER_50M = 'under_50m'
    INVESTMENT_50M_150M = '50m_150m'
    INVESTMENT_150M_300M = '150m_300m'
    INVESTMENT_ABOVE_300M = 'above_300m'

    INVESTMENT_RANGE_CHOICES = [
        (INVESTMENT_UNDER_50M, 'کمتر از ۵۰ میلیون تومان'),
        (INVESTMENT_50M_150M, '۵۰ تا ۱۵۰ میلیون تومان'),
        (INVESTMENT_150M_300M, '۱۵۰ تا ۳۰۰ میلیون تومان'),
        (INVESTMENT_ABOVE_300M, 'بیش از ۳۰۰ میلیون تومان'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار بررسی'),
        (STATUS_APPROVED, 'تایید شده'),
        (STATUS_REJECTED, 'رد شده'),
    ]

    tracking_code = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    franchise_type = models.CharField(max_length=10, choices=FRANCHISE_TYPE_CHOICES)
    investment_range = models.CharField(max_length=15, choices=INVESTMENT_RANGE_CHOICES)
    has_sales_experience = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_note = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'درخواست نمایندگی'
        verbose_name_plural = 'درخواست‌های نمایندگی'

    def __str__(self):
        return f"{self.tracking_code} — {self.full_name}"
