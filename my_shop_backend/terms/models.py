from django.db import models
from django.conf import settings


class TermsMetadata(models.Model):
    """Singleton row that holds version, last_updated, and hero/wallet content."""
    version = models.CharField(max_length=20, default='1.0')
    last_updated = models.CharField(max_length=20, blank=True)
    hero_title = models.CharField(max_length=300, blank=True)
    hero_subtitle = models.TextField(blank=True)
    wallet_title = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = 'Terms Metadata'
        verbose_name_plural = 'Terms Metadata'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Term(models.Model):
    question = models.TextField()
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Term'
        verbose_name_plural = 'Terms'

    def __str__(self):
        return f"Term #{self.order}: {self.question[:60]}"


class WalletTermsSection(models.Model):
    title = models.CharField(max_length=300)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Wallet Terms Section'
        verbose_name_plural = 'Wallet Terms Sections'

    def __str__(self):
        return self.title


class TermAcceptance(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='term_acceptances',
    )
    term_version = models.CharField(max_length=20)
    accepted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-accepted_at']
        verbose_name = 'Term Acceptance'
        verbose_name_plural = 'Term Acceptances'

    def __str__(self):
        return f"{self.user} accepted v{self.term_version}"
