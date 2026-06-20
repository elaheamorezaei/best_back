from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    icon = models.CharField(max_length=100, blank=True)
    is_main = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        related_name='children', on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=300, unique=True, null=True, blank=True, allow_unicode=True)
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    model = models.CharField(max_length=200, blank=True)
    brand = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    compare_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    min_stock = models.PositiveIntegerField(default=0)
    weight = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    star = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    off = models.PositiveSmallIntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)
    sales_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def final_price(self):
        if self.off:
            return int(self.price * (100 - self.off) / 100)
        return int(self.price)

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class ProductColor(models.Model):
    product = models.ForeignKey(Product, related_name='colors', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    hex = models.CharField(max_length=7)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} – {self.name}"


class ProductWarranty(models.Model):
    product = models.ForeignKey(Product, related_name='warranties', on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class ProductFeature(models.Model):
    product = models.ForeignKey(Product, related_name='features', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class ProductSpec(models.Model):
    product = models.ForeignKey(Product, related_name='specs', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class ProductIntro(models.Model):
    product = models.ForeignKey(Product, related_name='intro_paragraphs', on_delete=models.CASCADE)
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class ProductEditorialReview(models.Model):
    product = models.OneToOneField(
        Product, related_name='editorial_review', on_delete=models.CASCADE
    )
    text = models.TextField()
    pros = models.JSONField(default=list)
    cons = models.JSONField(default=list)

    def __str__(self):
        return f"Review for {self.product.name}"
