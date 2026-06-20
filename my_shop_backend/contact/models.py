from django.db import models
from django.conf import settings
from core.utils import to_persian_date


class ContactInfo(models.Model):
    """Singleton — اطلاعات تماس صفحه contact"""
    hero_text = models.TextField(blank=True)
    map_title = models.CharField(max_length=300, blank=True)
    map_subtitle = models.CharField(max_length=300, blank=True)
    map_iframe_src = models.TextField(blank=True)
    map_lat = models.FloatField(default=35.7)
    map_lng = models.FloatField(default=51.4)
    support_phones = models.JSONField(default=list)
    main_phone = models.CharField(max_length=30, blank=True)
    support_email = models.EmailField(blank=True)
    working_hours = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Contact Info'

    def __str__(self):
        return 'اطلاعات تماس'


class ContactSlider(models.Model):
    """Singleton — اسلایدر صفحه تماس"""
    image = models.ImageField(upload_to='contact/slider/')
    alt = models.CharField(max_length=200, default='تماس با بست')

    class Meta:
        verbose_name = 'Contact Slider'

    def __str__(self):
        return self.alt


class ContactSubject(models.Model):
    """موضوعات آماده فرم تماس"""
    label = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.label


class ContactTicket(models.Model):
    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'باز'),
        (STATUS_IN_PROGRESS, 'در حال بررسی'),
        (STATUS_RESOLVED, 'حل شده'),
        (STATUS_CLOSED, 'بسته'),
    ]

    STATUS_LABELS = {
        STATUS_OPEN: 'باز',
        STATUS_IN_PROGRESS: 'در حال بررسی',
        STATUS_RESOLVED: 'حل شده',
        STATUS_CLOSED: 'بسته',
    }

    ticket_id = models.CharField(max_length=20, unique=True)
    subject = models.CharField(max_length=300)
    order_number = models.CharField(max_length=50, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='contact_tickets',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticket_id} — {self.subject}"

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)

    @property
    def created_at_jalali(self):
        return to_persian_date(self.created_at)


class ContactTicketAttachment(models.Model):
    TYPE_IMAGE = 'image'
    TYPE_VIDEO = 'video'
    TYPE_CHOICES = [(TYPE_IMAGE, 'Image'), (TYPE_VIDEO, 'Video')]

    ticket = models.ForeignKey(
        ContactTicket, related_name='attachments', on_delete=models.CASCADE
    )
    file = models.FileField(upload_to='contact/attachments/')
    file_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.ticket.ticket_id} — {self.file_type}"


class ContactTicketResponse(models.Model):
    ticket = models.ForeignKey(
        ContactTicket, related_name='responses', on_delete=models.CASCADE
    )
    message = models.TextField()
    is_staff = models.BooleanField(default=False)
    staff_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.ticket.ticket_id} — {'staff' if self.is_staff else 'user'}"

    @property
    def created_at_jalali(self):
        return to_persian_date(self.created_at)
