from rest_framework import serializers
from .models import InsurancePlan, CartItem
from core.responses import build_absolute_image_url


class InsurancePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsurancePlan
        fields = ['id', 'name', 'price', 'duration_months', 'coverages']


class CartItemSerializer(serializers.ModelSerializer):
    productId = serializers.IntegerField(source='product.id', read_only=True)
    productName = serializers.CharField(source='product.name', read_only=True)
    productImage = serializers.SerializerMethodField()
    colorId = serializers.IntegerField(source='color.id', read_only=True)
    colorName = serializers.CharField(source='color.name', read_only=True)
    colorHex = serializers.CharField(source='color.hex', read_only=True)
    guaranteeId = serializers.IntegerField(source='guarantee.id', read_only=True)
    guaranteeText = serializers.CharField(source='guarantee.text', read_only=True)
    unitPrice = serializers.SerializerMethodField()
    discountedPrice = serializers.SerializerMethodField()
    insurance = InsurancePlanSerializer(read_only=True)
    listType = serializers.CharField(source='list_type', read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'productId', 'productName', 'productImage',
            'colorId', 'colorName', 'colorHex',
            'guaranteeId', 'guaranteeText',
            'unitPrice', 'discountedPrice',
            'quantity', 'insurance', 'listType',
        ]

    def get_productImage(self, obj):
        request = self.context.get('request')
        first = obj.product.images.first()
        if first:
            return build_absolute_image_url(request, first.image)
        return build_absolute_image_url(request, obj.product.image)

    def get_unitPrice(self, obj):
        return int(obj.product.price)

    def get_discountedPrice(self, obj):
        return obj.product.final_price
