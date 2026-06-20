from django.http import Http404
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from core.responses import success_response, data_response, error_detail_response
from .models import Category, Product
from .serializers import (
    CategoryDetailSerializer,
    MainCategorySerializer, ProductSerializer, ProductCardSerializer,
    ProductDetailSerializer, SimilarProductSerializer, ProductCompareSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name']

    def get_queryset(self):
        if self.action == 'retrieve':
            return Product.objects.select_related(
                'category', 'editorial_review'
            ).prefetch_related(
                'images', 'colors', 'warranties',
                'features', 'specs', 'intro_paragraphs', 'comments',
            )
        return Product.objects.all()

    def retrieve(self, request, *args, **kwargs):
        try:
            product = self.get_object()
        except Http404:
            return error_detail_response(404, "محصول یافت نشد", http_status=404)
        serializer = ProductDetailSerializer(product, context={'request': request})
        return data_response(serializer.data)


class MainCategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.filter(is_main=True)
        serializer = MainCategorySerializer(
            categories, many=True, context={'request': request}
        )
        return success_response(serializer.data)


class FeaturedProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.filter(is_featured=True).select_related('category')
        serializer = ProductCardSerializer(
            products, many=True, context={'request': request}
        )
        return success_response(serializer.data)


class BestSellersView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.filter(is_best_seller=True).select_related('category')
        serializer = ProductCardSerializer(
            products, many=True, context={'request': request}
        )
        return success_response(serializer.data)


class MostPopularView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.filter(is_popular=True).select_related('category')
        serializer = ProductCardSerializer(
            products, many=True, context={'request': request}
        )
        return success_response(serializer.data)


class SimilarProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return error_detail_response(404, "محصول یافت نشد", http_status=404)

        try:
            limit = max(1, int(request.query_params.get('limit', 8)))
        except (ValueError, TypeError):
            limit = 8
        similar = (
            Product.objects
            .filter(category=product.category)
            .exclude(pk=pk)
            .prefetch_related('images', 'colors')[:limit]
        )
        serializer = SimilarProductSerializer(
            similar, many=True, context={'request': request}
        )
        return data_response({'items': serializer.data})


class ProductCompareView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        ids_param = request.query_params.get('ids', '')
        if not ids_param:
            return error_detail_response(400, "پارامتر ids الزامی است", field="ids")

        try:
            ids = [int(i) for i in ids_param.split(',') if i.strip()]
        except ValueError:
            return error_detail_response(400, "فرمت ids نامعتبر است", field="ids")

        if len(ids) < 2:
            return error_detail_response(400, "حداقل ۲ محصول برای مقایسه لازم است", field="ids")

        products = (
            Product.objects
            .filter(pk__in=ids)
            .prefetch_related('images', 'specs')
        )
        serializer = ProductCompareSerializer(
            products, many=True, context={'request': request}
        )
        return data_response(serializer.data)


class ProductCompareDetailView(APIView):
    """GET /products/:id/compare — single product data for compare page."""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            product = Product.objects.prefetch_related('images', 'specs').get(pk=pk)
        except Product.DoesNotExist:
            return error_detail_response(404, "محصول یافت نشد", http_status=404)

        serializer = ProductCompareSerializer(product, context={'request': request})
        return data_response(serializer.data)
