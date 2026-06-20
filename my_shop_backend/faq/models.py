from django.db import models


class FAQCategory(models.Model):
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    @property
    def question_count(self):
        return self.faqs.filter(is_active=True).count()


class FAQ(models.Model):
    category = models.ForeignKey(
        FAQCategory, related_name='faqs', null=True, blank=True, on_delete=models.SET_NULL
    )
    question = models.TextField()
    answer = models.TextField()
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.question[:80]


class UserQuestion(models.Model):
    """سوالات ارسالی توسط کاربران"""
    STATUS_PENDING = 'pending'
    STATUS_ANSWERED = 'answered'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار بررسی'),
        (STATUS_ANSWERED, 'پاسخ داده شده'),
    ]

    question_id = models.CharField(max_length=30, unique=True)
    question = models.TextField()
    category = models.ForeignKey(
        FAQCategory, null=True, blank=True, on_delete=models.SET_NULL
    )
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.question_id} — {self.question[:60]}"
