from rest_framework import serializers
from core.responses import build_absolute_image_url
from .models import (
    Category, Product,
    ProductImage, ProductColor, ProductWarranty,
    ProductFeature, ProductSpec, ProductIntro, ProductEditorialReview,
)


# ─── Category ────────────────────────────────────────────────────────────────

class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MainCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    category = serializers.CharField(source='name')
    link = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'image', 'category', 'link']

    def get_image(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)

    def get_link(self, obj):
        return f"/category/{obj.slug}"


# ─── Product card (for list views) ───────────────────────────────────────────

class ProductSerializer(serializers.ModelSerializer):
    final_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductCardSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    final_price = serializers.IntegerField(read_only=True)
    price = serializers.IntegerField()
    star = serializers.FloatField()
    categoryId = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'slug', 'image', 'name', 'model', 'star', 'price', 'off', 'final_price', 'categoryId']

    def get_categoryId(self, obj):
        # تب‌های فیلتر دسته‌بندی فقط دسته‌های اصلی (is_main=True) رو نشون
        # می‌دن، ولی محصول ممکنه توی یک زیردسته باشه (مثلاً "AirPods" زیر
        # "صوتی و تصویری"). برای اینکه فیلتر کار کنه، اینجا به‌جای category
        # مستقیم محصول، از زنجیره‌ی parent بالا می‌ریم تا به دسته‌ی
        # ریشه/اصلی برسیم و همون id رو برمی‌گردونیم.
        category = obj.category
        while category and category.parent_id:
            category = category.parent
        return category.id if category else None

    def get_image(self, obj):
        request = self.context.get('request')
        # اول گالری واقعی محصول (ProductImage) رو چک می‌کنیم؛ محصولاتی که از
        # فرم ادمین ساخته می‌شن فقط همین رابطه رو پر می‌کنن، نه فیلد تکی و
        # قدیمی product.image. اگه گالری خالی بود (محصولات قدیمی‌تر)، به همون
        # فیلد قدیمی fallback می‌کنیم تا چیزی خراب نشه.
        first_img = obj.images.first()
        if first_img:
            return build_absolute_image_url(request, first_img.image)
        return build_absolute_image_url(request, obj.image)


# ─── Product detail (full product page) ──────────────────────────────────────

class ProductDetailSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    colors = serializers.SerializerMethodField()
    warranties = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    intro = serializers.SerializerMethodField()
    specs = serializers.SerializerMethodField()
    review = serializers.SerializerMethodField()
    reviewCount = serializers.SerializerMethodField()
    inStock = serializers.SerializerMethodField()
    selectedColor = serializers.SerializerMethodField()
    isInWishlist = serializers.SerializerMethodField()
    isNotifyRequested = serializers.SerializerMethodField()
    price = serializers.IntegerField()
    star = serializers.FloatField()

    class Meta:
        model = Product
        fields = [
            'id', 'slug', 'name', 'model', 'brand', 'short_description',
            'star', 'reviewCount', 'inStock', 'selectedColor', 'images',
            'price', 'off', 'colors', 'warranties', 'features', 'intro',
            'specs', 'review', 'isInWishlist', 'isNotifyRequested',
        ]

    def get_images(self, obj):
        request = self.context.get('request')
        images = [
            build_absolute_image_url(request, img.image)
            for img in obj.images.all()
        ]
        # fallback برای محصولاتی که هنوز گالری ندارن ولی فیلد تکی قدیمی پر شده
        if not images and obj.image:
            images = [build_absolute_image_url(request, obj.image)]
        return images

    def get_colors(self, obj):
        return [{'name': c.name, 'hex': c.hex} for c in obj.colors.all()]

    def get_warranties(self, obj):
        return [w.text for w in obj.warranties.all()]

    def get_features(self, obj):
        return [{'name': f.name, 'value': f.value} for f in obj.features.all()]

    def get_intro(self, obj):
        return [p.text for p in obj.intro_paragraphs.all()]

    def get_specs(self, obj):
        return [{'name': s.name, 'value': s.value} for s in obj.specs.all()]

    def get_review(self, obj):
        try:
            er = obj.editorial_review
            return {'text': er.text, 'pros': er.pros, 'cons': er.cons}
        except ProductEditorialReview.DoesNotExist:
            return None

    def get_reviewCount(self, obj):
        return obj.comments.count()

    def get_inStock(self, obj):
        return obj.stock > 0

    def get_selectedColor(self, obj):
        color = obj.colors.filter(is_default=True).first() or obj.colors.first()
        return color.name if color else None

    def get_isInWishlist(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.wishlists.filter(user=request.user).exists()
        return False

    def get_isNotifyRequested(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.stock_notifications.filter(user=request.user).exists()
        return False


# ─── Similar / Compare ───────────────────────────────────────────────────────

class SimilarProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    star = serializers.FloatField()
    price = serializers.IntegerField()
    colors = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'slug', 'name', 'model', 'image', 'star', 'price', 'off', 'colors']

    def get_image(self, obj):
        request = self.context.get('request')
        first_img = obj.images.first()
        if first_img:
            return build_absolute_image_url(request, first_img.image)
        return build_absolute_image_url(request, obj.image)

    def get_colors(self, obj):
        return [{'hex': c.hex} for c in obj.colors.all()]


class ProductCompareSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    price = serializers.IntegerField()
    star = serializers.FloatField()
    specs = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'slug', 'name', 'model', 'image', 'price', 'off', 'star', 'specs']

    def get_image(self, obj):
        request = self.context.get('request')
        first_img = obj.images.first()
        if first_img:
            return build_absolute_image_url(request, first_img.image)
        return build_absolute_image_url(request, obj.image)

    def get_specs(self, obj):
        return [{'name': s.name, 'value': s.value} for s in obj.specs.all()]