import json
from urllib.parse import urlparse

from django.conf import settings
from django.db.models.deletion import ProtectedError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from admin_api.permissions import IsAdminUser
from products.models import (
    Product, Category, ProductImage,
    ProductColor, ProductSpec, ProductFeature, ProductWarranty,
)
from core.responses import build_absolute_image_url


def _serialize_product(product, request):
    images = [
        {
            'id': img.id,
            'url': build_absolute_image_url(request, img.image),
            'alt': '',
            'isPrimary': img.order == 0,
            'order': img.order,
        }
        for img in product.images.all()
    ]
    colors = [
        {'id': c.id, 'name': c.name, 'value': c.hex, 'stock': None}
        for c in product.colors.all()
    ]
    specs = [
        {'id': s.id, 'name': s.name, 'value': s.value, 'unit': None}
        for s in product.specs.all()
    ]
    features = [
        {'id': f.id, 'name': f.name, 'value': f.value}
        for f in product.features.all()
    ]
    warranties = [
        {'id': w.id, 'text': w.text}
        for w in product.warranties.all()
    ]
    return {
        'id': product.id,
        'name': product.name,
        'slug': product.slug or '',
        'sku': product.sku or '',
        'description': product.description,
        'shortDescription': product.short_description,
        'price': int(product.price),
        'comparePrice': int(product.compare_price) if product.compare_price else None,
        'costPrice': int(product.cost_price) if product.cost_price else None,
        'stock': product.stock,
        'minStock': product.min_stock,
        'weight': product.weight,
        'categoryId': product.category_id,
        'categoryName': product.category.name,
        'tags': product.tags or [],
        'images': images,
        'variants': colors,
        'attributes': specs,
        'features': features,
        'warranties': warranties,
        'isActive': product.is_active,
        'isFeatured': product.is_featured,
        'isNew': product.is_new,
        'isSale': product.is_sale,
        'rating': float(product.star),
        'reviewCount': product.comments.count(),
        'salesCount': product.sales_count,
        'createdAt': product.created_at.isoformat(),
    }


def _relative_media_path(url):
    """
    ورودی می‌تونه یک URL کامل باشه (مثل خروجی endpoint آپلود:
    http://localhost:8000/media/products/abc.jpg) یا از قبل یک مسیر نسبی.
    خروجی همیشه مسیر نسبی‌ای‌ست که ImageField انتظارش رو داره
    (مثل 'products/abc.jpg'), بدون دامنه و بدون پیشوند MEDIA_URL.
    """
    if not url:
        return ''
    path = urlparse(url).path or url
    media_url = settings.MEDIA_URL or '/media/'
    if path.startswith(media_url):
        path = path[len(media_url):]
    return path.lstrip('/')


def _sync_product_images(product, images_data):
    """
    آرایه‌ی images (لیستی از dict با کلیدهای id, url, order, ...) که از
    فرانت می‌رسه رو با رکوردهای واقعی ProductImage هماهنگ می‌کنه:
    - آیتم‌هایی که id دارن و از قبل وجود دارن → فقط order به‌روزرسانی می‌شه
    - آیتم‌های جدید (بدون id، یا id نامعتبر) → یک ProductImage جدید ساخته می‌شه
      و image به مسیر نسبیِ فایلِ از قبل آپلودشده وصل می‌شه
    - رکوردهایی که دیگه در لیست جدید نیستن → حذف می‌شن (هم رکورد هم فایل)
    """
    if isinstance(images_data, str):
        try:
            images_data = json.loads(images_data)
        except Exception:
            images_data = []
    if not isinstance(images_data, list):
        images_data = []

    existing_by_id = {img.id: img for img in product.images.all()}
    keep_ids = set()

    for order, item in enumerate(images_data):
        if not isinstance(item, dict):
            continue
        img_id = item.get('id')
        url = item.get('url', '')

        if img_id in existing_by_id:
            pi = existing_by_id[img_id]
            if pi.order != order:
                pi.order = order
                pi.save(update_fields=['order'])
            keep_ids.add(img_id)
        else:
            rel_path = _relative_media_path(url)
            if not rel_path:
                continue
            pi = ProductImage.objects.create(
                product=product, image=rel_path, order=order
            )
            keep_ids.add(pi.id)

    for img_id, pi in existing_by_id.items():
        if img_id not in keep_ids:
            pi.image.delete(save=False)
            pi.delete()


def _sync_variants(product, variants_data):
    """variants از frontend = رنگ‌ها → ذخیره در ProductColor"""
    if isinstance(variants_data, str):
        try:
            variants_data = json.loads(variants_data)
        except Exception:
            variants_data = []
    if not isinstance(variants_data, list):
        variants_data = []

    existing_by_id = {c.id: c for c in ProductColor.objects.filter(product=product)}
    keep_ids = set()

    for item in variants_data:
        if not isinstance(item, dict):
            continue
        item_id = item.get('id')
        name = (item.get('name') or '').strip()
        hex_val = (item.get('value') or '').strip()

        if item_id and item_id in existing_by_id:
            color = existing_by_id[item_id]
            update = []
            if name and color.name != name:
                color.name = name
                update.append('name')
            if hex_val and color.hex != hex_val:
                color.hex = hex_val
                update.append('hex')
            if update:
                color.save(update_fields=update)
            keep_ids.add(item_id)
        else:
            if name:
                color = ProductColor.objects.create(product=product, name=name, hex=hex_val or '')
                keep_ids.add(color.id)

    for cid, color in existing_by_id.items():
        if cid not in keep_ids:
            color.delete()


def _sync_attributes(product, attributes_data):
    """attributes از frontend = ویژگی‌ها → ذخیره در ProductSpec"""
    if isinstance(attributes_data, str):
        try:
            attributes_data = json.loads(attributes_data)
        except Exception:
            attributes_data = []
    if not isinstance(attributes_data, list):
        attributes_data = []

    existing_by_id = {s.id: s for s in ProductSpec.objects.filter(product=product)}
    keep_ids = set()

    for order, item in enumerate(attributes_data):
        if not isinstance(item, dict):
            continue
        item_id = item.get('id')
        name = (item.get('name') or '').strip()
        value = (item.get('value') or '').strip()

        if item_id and item_id in existing_by_id:
            spec = existing_by_id[item_id]
            update = []
            if name and spec.name != name:
                spec.name = name
                update.append('name')
            if spec.value != value:
                spec.value = value
                update.append('value')
            if spec.order != order:
                spec.order = order
                update.append('order')
            if update:
                spec.save(update_fields=update)
            keep_ids.add(item_id)
        else:
            if name:
                spec = ProductSpec.objects.create(product=product, name=name, value=value, order=order)
                keep_ids.add(spec.id)

    for sid, spec in existing_by_id.items():
        if sid not in keep_ids:
            spec.delete()


def _sync_features(product, features_data):
    if isinstance(features_data, str):
        try:
            features_data = json.loads(features_data)
        except Exception:
            features_data = []
    if not isinstance(features_data, list):
        features_data = []

    existing_by_id = {f.id: f for f in ProductFeature.objects.filter(product=product)}
    keep_ids = set()

    for order, item in enumerate(features_data):
        if not isinstance(item, dict):
            continue
        item_id = item.get('id')
        name = (item.get('name') or '').strip()
        value = (item.get('value') or '').strip()

        if item_id and item_id in existing_by_id:
            feat = existing_by_id[item_id]
            update = []
            if name and feat.name != name:
                feat.name = name
                update.append('name')
            if feat.value != value:
                feat.value = value
                update.append('value')
            if feat.order != order:
                feat.order = order
                update.append('order')
            if update:
                feat.save(update_fields=update)
            keep_ids.add(item_id)
        else:
            if name:
                feat = ProductFeature.objects.create(product=product, name=name, value=value, order=order)
                keep_ids.add(feat.id)

    for fid, feat in existing_by_id.items():
        if fid not in keep_ids:
            feat.delete()


def _sync_warranties(product, warranties_data):
    if isinstance(warranties_data, str):
        try:
            warranties_data = json.loads(warranties_data)
        except Exception:
            warranties_data = []
    if not isinstance(warranties_data, list):
        warranties_data = []

    existing_by_id = {w.id: w for w in ProductWarranty.objects.filter(product=product)}
    keep_ids = set()

    for order, item in enumerate(warranties_data):
        if isinstance(item, str):
            item = {'text': item}
        if not isinstance(item, dict):
            continue
        item_id = item.get('id')
        text = (item.get('text') or '').strip()

        if item_id and item_id in existing_by_id:
            war = existing_by_id[item_id]
            if text and war.text != text:
                war.text = text
                war.save(update_fields=['text'])
            keep_ids.add(item_id)
        else:
            if text:
                war = ProductWarranty.objects.create(product=product, text=text, order=order)
                keep_ids.add(war.id)

    for wid, war in existing_by_id.items():
        if wid not in keep_ids:
            war.delete()


class AdminProductListView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = Product.objects.select_related('category').prefetch_related('images', 'colors', 'specs', 'features', 'warranties', 'comments')

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(name__icontains=search)

        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)

        if request.query_params.get('isActive') == 'true':
            qs = qs.filter(is_active=True)
        elif request.query_params.get('isActive') == 'false':
            qs = qs.filter(is_active=False)

        if request.query_params.get('isFeatured') == 'true':
            qs = qs.filter(is_featured=True)

        if request.query_params.get('lowStock') == 'true':
            from django.db.models import F
            qs = qs.filter(stock__lte=F('min_stock'))

        ordering = request.query_params.get('ordering', '-id')
        django_ordering = ordering.replace('createdAt', 'created_at').replace('name', 'name')
        try:
            qs = qs.order_by(django_ordering)
        except Exception:
            qs = qs.order_by('-id')

        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = max(1, min(100, int(request.query_params.get('pageSize', 20))))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        total = qs.count()
        start = (page - 1) * page_size
        items = list(qs[start:start + page_size])

        return Response({
            'results': [_serialize_product(p, request) for p in items],
            'count': total,
            'next': None,
            'previous': None,
        })

    def post(self, request):
        data = request.data
        name = data.get('name', '').strip()
        if not name:
            return Response({'error': {'message': 'نام محصول الزامی است', 'code': 'MISSING_NAME'}}, status=400)

        category_id = data.get('categoryId')
        if not category_id:
            return Response({'error': {'message': 'دسته‌بندی الزامی است', 'code': 'MISSING_CATEGORY'}}, status=400)

        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return Response({'error': {'message': 'دسته‌بندی یافت نشد', 'code': 'CATEGORY_NOT_FOUND'}}, status=404)

        price = data.get('price', 0)
        try:
            price = float(price)
        except (ValueError, TypeError):
            return Response({'error': {'message': 'قیمت نامعتبر است', 'code': 'INVALID_PRICE'}}, status=400)

        tags = data.get('tags', '[]')
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except Exception:
                tags = []

        product = Product.objects.create(
            name=name,
            slug=data.get('slug') or None,
            sku=data.get('sku') or None,
            description=data.get('description', ''),
            short_description=data.get('shortDescription', ''),
            price=price,
            compare_price=data.get('comparePrice') or None,
            cost_price=data.get('costPrice') or None,
            stock=int(data.get('stock', 0)),
            min_stock=int(data.get('minStock', 0)),
            weight=data.get('weight') or None,
            category=category,
            tags=tags,
            is_active=str(data.get('isActive', 'true')).lower() != 'false',
            is_featured=str(data.get('isFeatured', 'false')).lower() == 'true',
            is_new=str(data.get('isNew', 'false')).lower() == 'true',
            is_sale=str(data.get('isSale', 'false')).lower() == 'true',
        )

        if 'image' in request.FILES:
            product.image = request.FILES['image']
            product.save(update_fields=['image'])

        if 'images' in data:
            _sync_product_images(product, data['images'])
        if 'variants' in data:
            _sync_variants(product, data['variants'])
        if 'attributes' in data:
            _sync_attributes(product, data['attributes'])
        if 'features' in data:
            _sync_features(product, data['features'])
        if 'warranties' in data:
            _sync_warranties(product, data['warranties'])

        product = Product.objects.select_related('category').prefetch_related(
            'images', 'colors', 'specs', 'features', 'warranties', 'comments'
        ).get(pk=product.pk)
        return Response(_serialize_product(product, request), status=201)


class AdminProductDetailView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get(self, pk):
        try:
            return Product.objects.select_related('category').prefetch_related('images', 'colors', 'specs', 'features', 'warranties', 'comments').get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self._get(pk)
        if not product:
            return Response({'error': {'message': 'محصول یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        return Response(_serialize_product(product, request))

    def patch(self, request, pk):
        product = self._get(pk)
        if not product:
            return Response({'error': {'message': 'محصول یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        data = request.data
        update_fields = []

        str_fields = [('name', 'name'), ('slug', 'slug'), ('sku', 'sku'),
                      ('description', 'description'), ('shortDescription', 'short_description')]
        for api_key, model_field in str_fields:
            if api_key in data:
                setattr(product, model_field, data[api_key])
                update_fields.append(model_field)

        num_fields = [('price', 'price'), ('comparePrice', 'compare_price'),
                      ('costPrice', 'cost_price'), ('stock', 'stock'), ('minStock', 'min_stock'), ('weight', 'weight')]
        for api_key, model_field in num_fields:
            if api_key in data:
                val = data[api_key]
                setattr(product, model_field, float(val) if val not in (None, '') else None)
                update_fields.append(model_field)

        if 'categoryId' in data:
            try:
                product.category = Category.objects.get(pk=data['categoryId'])
                update_fields.append('category')
            except Category.DoesNotExist:
                pass

        for api_key, model_field in [('isActive', 'is_active'), ('isFeatured', 'is_featured'),
                                      ('isNew', 'is_new'), ('isSale', 'is_sale')]:
            if api_key in data:
                setattr(product, model_field, str(data[api_key]).lower() not in ('false', '0'))
                update_fields.append(model_field)

        if 'tags' in data:
            tags = data['tags']
            if isinstance(tags, str):
                try:
                    tags = json.loads(tags)
                except Exception:
                    tags = []
            product.tags = tags
            update_fields.append('tags')

        if 'image' in request.FILES:
            product.image = request.FILES['image']
            update_fields.append('image')

        if update_fields:
            product.save(update_fields=update_fields)

        # گالری تصاویر (ProductImage) یک رابطه‌ی جداست، پس مستقل از
        # update_fields بالا، اینجا با رکوردهای واقعی هماهنگ می‌شه.
        if 'images' in data:
            _sync_product_images(product, data['images'])
        if 'variants' in data:
            _sync_variants(product, data['variants'])
        if 'attributes' in data:
            _sync_attributes(product, data['attributes'])
        if 'features' in data:
            _sync_features(product, data['features'])
        if 'warranties' in data:
            _sync_warranties(product, data['warranties'])

        product = Product.objects.select_related('category').prefetch_related(
            'images', 'colors', 'specs', 'features', 'warranties', 'comments'
        ).get(pk=product.pk)
        return Response(_serialize_product(product, request))

    def delete(self, request, pk):
        product = self._get(pk)
        if not product:
            return Response({'error': {'message': 'محصول یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        try:
            product.delete()
        except ProtectedError:
            return Response(
                {'error': {'message': 'این محصول در سفارشات ثبت‌شده استفاده شده و قابل حذف نیست', 'code': 'PRODUCT_IN_USE'}},
                status=409,
            )
        return Response(status=204)


class AdminProductToggleActiveView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': {'message': 'محصول یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        product.is_active = not product.is_active
        product.save(update_fields=['is_active'])
        return Response({'isActive': product.is_active})


class AdminProductToggleFeaturedView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': {'message': 'محصول یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        product.is_featured = not product.is_featured
        product.save(update_fields=['is_featured'])
        return Response({'isFeatured': product.is_featured})


class AdminProductBulkDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': {'message': 'ids الزامی است', 'code': 'MISSING_IDS'}}, status=400)

        skipped = []
        deleted = 0
        for pid in ids:
            try:
                count, _ = Product.objects.filter(pk=pid).delete()
                deleted += count
            except ProtectedError:
                skipped.append(pid)

        return Response({'deleted': deleted, 'skipped': skipped})