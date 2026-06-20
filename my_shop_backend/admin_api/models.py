from django.db import models
from django.conf import settings


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default='فروشگاه آنلاین')
    site_description = models.TextField(blank=True)
    site_keywords = models.JSONField(default=list, blank=True)
    logo = models.ImageField(upload_to='settings/', null=True, blank=True)
    favicon = models.ImageField(upload_to='settings/', null=True, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    instagram = models.CharField(max_length=200, blank=True)
    telegram = models.CharField(max_length=200, blank=True)
    whatsapp = models.CharField(max_length=50, blank=True)
    google_analytics_id = models.CharField(max_length=50, blank=True)
    google_tag_manager_id = models.CharField(max_length=50, blank=True)
    robots_txt = models.TextField(blank=True, default='User-agent: *\nAllow: /')
    maintenance_mode = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.site_name


class ThemeSettings(models.Model):
    primary = models.CharField(max_length=20, default='#ef4444')
    secondary = models.CharField(max_length=20, default='#f59e0b')
    accent = models.CharField(max_length=20, default='#8b5cf6')
    neutral = models.CharField(max_length=20, default='#6b7280')
    base = models.CharField(max_length=20, default='#ffffff')
    info = models.CharField(max_length=20, default='#3b82f6')
    success = models.CharField(max_length=20, default='#22c55e')
    warning = models.CharField(max_length=20, default='#f59e0b')
    error = models.CharField(max_length=20, default='#ef4444')
    radius = models.CharField(max_length=20, default='0.75rem')
    font_family = models.CharField(max_length=100, default='Vazir')
    mode = models.CharField(max_length=10, default='light')

    class Meta:
        verbose_name = 'Theme Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f'Theme ({self.mode})'


class SEOPageSettings(models.Model):
    page = models.CharField(max_length=100)
    path = models.CharField(max_length=200, unique=True)
    meta_title = models.CharField(max_length=300, blank=True)
    meta_description = models.TextField(blank=True)
    keywords = models.JSONField(default=list, blank=True)
    og_image = models.CharField(max_length=500, blank=True)
    no_index = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'SEO Page Settings'

    def __str__(self):
        return f'{self.page} ({self.path})'


class OrderNote(models.Model):
    order = models.ForeignKey(
        'orders.Order', related_name='notes', on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    text = models.TextField()
    is_admin = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Note on order {self.order_id}'
