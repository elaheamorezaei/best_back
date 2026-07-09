from django.db.models.deletion import ProtectedError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from admin_api.permissions import IsAdminUser
from products.models import Category
from core.responses import build_absolute_image_url


def _serialize_category(cat, request):
    return {
        'id': cat.id,
        'name': cat.name,
        'slug': cat.slug,
        'description': cat.description,
        'image': build_absolute_image_url(request, cat.image),
        'parentId': cat.parent_id,
        'parentName': cat.parent.name if cat.parent else None,
        'order': cat.order,
        'isActive': cat.is_active,
        'productCount': cat.products.count(),
        'createdAt': None,
    }


def _collect_with_descendants(cat):
    """
    شناسه‌ی این دسته + همه‌ی زیردسته‌ها (در هر عمق) را برمی‌گرداند، تا هنگام
    حذف، کل زیردرخت با هم پاک شود (نه اینکه فقط parent آن‌ها خالی بماند).
    """
    ids = [cat.id]
    for child in cat.children.all():
        ids.extend(_collect_with_descendants(child))
    return ids


class AdminCategoryListView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = Category.objects.select_related('parent').prefetch_related('products')

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(name__icontains=search)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = max(1, min(100, int(request.query_params.get('pageSize', 20))))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        total = qs.count()
        start = (page - 1) * page_size
        items = list(qs[start:start + page_size])

        return Response({
            'results': [_serialize_category(c, request) for c in items],
            'count': total,
            'next': None,
            'previous': None,
        })

    def post(self, request):
        data = request.data
        name = data.get('name', '').strip()
        slug = data.get('slug', '').strip()
        if not name or not slug:
            return Response({'error': {'message': 'نام و slug الزامی است', 'code': 'MISSING_FIELDS'}}, status=400)

        if Category.objects.filter(slug=slug).exists():
            return Response({'error': {'message': 'slug تکراری است', 'code': 'DUPLICATE_SLUG'}}, status=409)

        parent_id = data.get('parentId')
        parent = None
        if parent_id:
            try:
                parent = Category.objects.get(pk=parent_id)
            except Category.DoesNotExist:
                return Response({'error': {'message': 'دسته والد یافت نشد', 'code': 'PARENT_NOT_FOUND'}}, status=404)

        cat = Category.objects.create(
            name=name,
            slug=slug,
            description=data.get('description', ''),
            parent=parent,
            order=int(data.get('order', 0)),
            is_active=str(data.get('isActive', 'true')).lower() != 'false',
        )

        if 'image' in request.FILES:
            cat.image = request.FILES['image']
            cat.save(update_fields=['image'])

        cat.refresh_from_db()
        return Response(_serialize_category(cat, request), status=201)


class AdminCategoryAllView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        cats = Category.objects.select_related('parent').all()
        return Response([_serialize_category(c, request) for c in cats])


class AdminCategoryDetailView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get(self, pk):
        try:
            return Category.objects.select_related('parent').prefetch_related('products').get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        cat = self._get(pk)
        if not cat:
            return Response({'error': {'message': 'دسته‌بندی یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        return Response(_serialize_category(cat, request))

    def patch(self, request, pk):
        cat = self._get(pk)
        if not cat:
            return Response({'error': {'message': 'دسته‌بندی یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        data = request.data
        update_fields = []

        for api_key, model_field in [('name', 'name'), ('slug', 'slug'), ('description', 'description')]:
            if api_key in data:
                if api_key == 'slug' and Category.objects.filter(slug=data[api_key]).exclude(pk=pk).exists():
                    return Response({'error': {'message': 'slug تکراری است', 'code': 'DUPLICATE_SLUG'}}, status=409)
                setattr(cat, model_field, data[api_key])
                update_fields.append(model_field)

        if 'order' in data:
            cat.order = int(data['order'])
            update_fields.append('order')

        if 'isActive' in data:
            cat.is_active = str(data['isActive']).lower() not in ('false', '0')
            update_fields.append('is_active')

        if 'parentId' in data:
            pid = data['parentId']
            if pid:
                try:
                    cat.parent = Category.objects.get(pk=pid)
                except Category.DoesNotExist:
                    pass
            else:
                cat.parent = None
            update_fields.append('parent')

        if 'image' in request.FILES:
            cat.image = request.FILES['image']
            update_fields.append('image')

        if update_fields:
            cat.save(update_fields=update_fields)

        cat.refresh_from_db()
        return Response(_serialize_category(cat, request))

    def delete(self, request, pk):
        cat = self._get(pk)
        if not cat:
            return Response({'error': {'message': 'دسته‌بندی یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        ids_to_delete = _collect_with_descendants(cat)
        try:
            Category.objects.filter(pk__in=ids_to_delete).delete()
        except ProtectedError:
            return Response(
                {'error': {'message': 'این دسته‌بندی دارای محصولاتی است که در سفارشات ثبت‌شده استفاده شده‌اند و قابل حذف نیست', 'code': 'CATEGORY_IN_USE'}},
                status=409,
            )
        return Response(status=204)


class AdminCategoryReorderView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        items = request.data.get('items', [])
        updated = 0
        for item in items:
            count = Category.objects.filter(pk=item['id']).update(order=item['order'])
            updated += count
        return Response({'updated': updated})