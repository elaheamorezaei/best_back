from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from products.models import Product, Category
from core.responses import build_absolute_image_url
from .models import CompareDescription

# Feature values that mean "does not have this feature"
_FALSY_VALUES = {'', 'ندارد', 'خیر', 'false', 'no', '0', 'نه', 'n', 'f'}


def _has_feature(value: str) -> bool:
    return value.strip().lower() not in _FALSY_VALUES


def _serialize_product(product, request):
    """Serialize a single product using its own specs/features (no alignment)."""
    return {
        'id': product.id,
        'image': build_absolute_image_url(request, product.image),
        'name': product.name,
        'model': product.model,
        'star': float(product.star),
        'price': int(product.price),
        'off': product.off,
        'colors': [c.hex for c in product.colors.all()],
        'specs': [
            {'name': s.name, 'value': s.value if s.value else None}
            for s in product.specs.all()
        ],
        'features': [
            {'name': f.name, 'hasFeature': _has_feature(f.value)}
            for f in product.features.all()
        ],
    }


def _align_and_serialize(products, request):
    """Serialize multiple products with aligned specs/features for compare table."""
    # Collect all unique spec/feature names in first-appearance order
    all_spec_names = list(dict.fromkeys(
        spec.name
        for p in products
        for spec in p.specs.all()
    ))
    all_feature_names = list(dict.fromkeys(
        feat.name
        for p in products
        for feat in p.features.all()
    ))

    result = []
    for product in products:
        spec_map = {s.name: s.value for s in product.specs.all()}
        feature_map = {f.name: f.value for f in product.features.all()}

        result.append({
            'id': product.id,
            'image': build_absolute_image_url(request, product.image),
            'name': product.name,
            'model': product.model,
            'star': float(product.star),
            'price': int(product.price),
            'off': product.off,
            'colors': [c.hex for c in product.colors.all()],
            'specs': [
                {'name': name, 'value': spec_map.get(name) or None}
                for name in all_spec_names
            ],
            'features': [
                {
                    'name': name,
                    'hasFeature': (
                        _has_feature(feature_map[name])
                        if name in feature_map
                        else False
                    ),
                }
                for name in all_feature_names
            ],
        })

    return result


class CompareProductListView(APIView):
    """GET /compare/products — paginated product list for a category (picker UI)."""
    permission_classes = [AllowAny]

    def get(self, request):
        category_slug = request.query_params.get('category', '').strip()
        if not category_slug:
            return Response(
                {'error': 'MISSING_CATEGORY', 'message': 'پارامتر category الزامی است'},
                status=400,
            )

        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return Response(
                {'error': 'CATEGORY_NOT_FOUND', 'message': 'دسته‌بندی یافت نشد'},
                status=404,
            )

        search = request.query_params.get('search', '').strip()
        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1
        try:
            limit = min(50, max(1, int(request.query_params.get('limit', 20))))
        except (ValueError, TypeError):
            limit = 20

        qs = (
            Product.objects
            .filter(category=category)
            .prefetch_related('colors', 'specs', 'features')
        )
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(model__icontains=search))

        total = qs.count()
        total_pages = max(1, (total + limit - 1) // limit)
        items = list(qs[(page - 1) * limit: page * limit])

        return Response({
            'items': [_serialize_product(p, request) for p in items],
            'total': total,
            'page': page,
            'totalPages': total_pages,
        })


class CompareView(APIView):
    """GET /compare?ids=10,11,12 — full aligned compare data for selected products."""
    permission_classes = [AllowAny]

    def get(self, request):
        ids_param = request.query_params.get('ids', '').strip()
        if not ids_param:
            return Response(
                {'error': 'MISSING_IDS', 'message': 'پارامتر ids الزامی است'},
                status=400,
            )

        try:
            ids_raw = [int(i.strip()) for i in ids_param.split(',') if i.strip()]
            if not ids_raw:
                raise ValueError
            # deduplicate while preserving order
            seen = set()
            ids = [x for x in ids_raw if not (x in seen or seen.add(x))]
        except (ValueError, TypeError):
            return Response(
                {'error': 'INVALID_IDS', 'message': 'فرمت ids نامعتبر است'},
                status=400,
            )

        if len(ids) < 2:
            return Response(
                {'error': 'TOO_FEW_PRODUCTS', 'message': 'حداقل ۲ محصول برای مقایسه انتخاب کنید'},
                status=400,
            )

        if len(ids) > 4:
            return Response(
                {'error': 'TOO_MANY_PRODUCTS', 'message': 'حداکثر ۴ محصول قابل مقایسه است'},
                status=400,
            )

        products_map = {
            p.id: p
            for p in Product.objects
            .filter(pk__in=ids)
            .prefetch_related('colors', 'specs', 'features')
        }

        missing = [i for i in ids if i not in products_map]
        if missing:
            return Response(
                {
                    'error': 'PRODUCTS_NOT_FOUND',
                    'message': 'یک یا چند محصول یافت نشد',
                    'missingIds': missing,
                },
                status=404,
            )

        # Preserve the order the caller sent
        ordered = [products_map[i] for i in ids]
        return Response({'products': _align_and_serialize(ordered, request)})


class CompareDescriptionView(APIView):
    """GET /compare/description?category=... — text description for compare page footer."""
    permission_classes = [AllowAny]

    def get(self, request):
        category_slug = request.query_params.get('category', '').strip()
        if not category_slug:
            return Response(
                {'error': 'MISSING_CATEGORY', 'message': 'پارامتر category الزامی است'},
                status=400,
            )

        try:
            category = Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return Response(
                {'error': 'CATEGORY_NOT_FOUND', 'message': 'دسته‌بندی یافت نشد'},
                status=404,
            )

        try:
            desc = CompareDescription.objects.get(category=category)
        except CompareDescription.DoesNotExist:
            return Response(
                {'error': 'DESCRIPTION_NOT_FOUND', 'message': 'توضیحاتی برای این دسته‌بندی یافت نشد'},
                status=404,
            )

        return Response({'title': desc.title, 'content': desc.content})
