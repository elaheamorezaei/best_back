from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_PENDING = 'pending_payment'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'payment_failed'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Payment'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FAILED, 'Payment Failed'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    PAYMENT_ONLINE = 'online'
    PAYMENT_COD = 'cod'
    PAYMENT_CHOICES = [(PAYMENT_ONLINE, 'Online'), (PAYMENT_COD, 'Cash on Delivery')]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.PROTECT
    )
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # Address snapshot
    address = models.ForeignKey(
        'addresses.Address', null=True, on_delete=models.SET_NULL
    )
    address_snapshot = models.JSONField(default=dict)

    # Delivery
    delivery_type = models.CharField(max_length=20, default='normal')
    delivery_date = models.CharField(max_length=20, blank=True)
    delivery_slot = models.ForeignKey(
        'delivery.DeliveryTimeSlot', null=True, blank=True, on_delete=models.SET_NULL
    )
    delivery_cost = models.PositiveIntegerField(default=0)

    # Payment
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default=PAYMENT_ONLINE)
    payment_token = models.CharField(max_length=200, blank=True)
    payment_tracking_code = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Discounts
    discount_code = models.ForeignKey(
        'discounts.DiscountCode', null=True, blank=True, on_delete=models.SET_NULL
    )
    gift_card = models.ForeignKey(
        'discounts.GiftCard', null=True, blank=True, on_delete=models.SET_NULL
    )

    # Totals
    products_total = models.PositiveIntegerField(default=0)
    insurance_total = models.PositiveIntegerField(default=0)
    discount_amount = models.PositiveIntegerField(default=0)
    discount_code_amount = models.PositiveIntegerField(default=0)
    gift_card_amount = models.PositiveIntegerField(default=0)
    final_total = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} — {self.user}"

    @property
    def order_id(self):
        return f"ORD-{self.pk:06d}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)
    product_image = models.CharField(max_length=500, blank=True)
    color_name = models.CharField(max_length=100, blank=True)
    guarantee_text = models.CharField(max_length=300, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()
    insurance_name = models.CharField(max_length=200, blank=True)
    insurance_price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"
