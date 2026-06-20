from rest_framework.views import APIView
from rest_framework.response import Response

from admin_api.permissions import IsAdminUser
from faq.models import FAQCategory, FAQ


def _serialize_category(cat):
    return {
        'id': cat.id,
        'name': cat.name,
        'icon': cat.icon,
        'order': cat.order,
        'isActive': True,
    }


def _serialize_faq(faq):
    return {
        'id': faq.id,
        'question': faq.question,
        'answer': faq.answer,
        'categoryId': faq.category_id,
        'categoryName': faq.category.name if faq.category else None,
        'order': faq.order,
        'isActive': faq.is_active,
        'viewCount': faq.helpful_count,
    }


class AdminFAQCategoryListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        cats = FAQCategory.objects.all().order_by('order')
        return Response([_serialize_category(c) for c in cats])

    def post(self, request):
        data = request.data
        name = data.get('name', '').strip()
        if not name:
            return Response({'error': {'message': 'نام الزامی است', 'code': 'MISSING_NAME'}}, status=400)
        cat = FAQCategory.objects.create(
            name=name,
            icon=data.get('icon', ''),
            order=int(data.get('order', 0)),
        )
        return Response(_serialize_category(cat), status=201)


class AdminFAQCategoryDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get(self, pk):
        try:
            return FAQCategory.objects.get(pk=pk)
        except FAQCategory.DoesNotExist:
            return None

    def patch(self, request, pk):
        cat = self._get(pk)
        if not cat:
            return Response({'error': {'message': 'دسته یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        data = request.data
        update_fields = []
        for key in ['name', 'icon']:
            if key in data:
                setattr(cat, key, data[key])
                update_fields.append(key)
        if 'order' in data:
            cat.order = int(data['order'])
            update_fields.append('order')
        if update_fields:
            cat.save(update_fields=update_fields)
        return Response(_serialize_category(cat))

    def delete(self, request, pk):
        cat = self._get(pk)
        if not cat:
            return Response({'error': {'message': 'دسته یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        cat.delete()
        return Response(status=204)


class AdminFAQListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = FAQ.objects.select_related('category')

        category_id = request.query_params.get('categoryId')
        if category_id:
            qs = qs.filter(category_id=category_id)

        if request.query_params.get('isActive') == 'true':
            qs = qs.filter(is_active=True)
        elif request.query_params.get('isActive') == 'false':
            qs = qs.filter(is_active=False)

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(question__icontains=search)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = max(1, min(100, int(request.query_params.get('pageSize', 20))))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        total = qs.count()
        start = (page - 1) * page_size
        items = list(qs[start:start + page_size])

        return Response({
            'results': [_serialize_faq(f) for f in items],
            'count': total,
            'next': None,
            'previous': None,
        })

    def post(self, request):
        data = request.data
        question = data.get('question', '').strip()
        answer = data.get('answer', '').strip()
        if not question or not answer:
            return Response({'error': {'message': 'سوال و جواب الزامی است', 'code': 'MISSING_FIELDS'}}, status=400)

        category = None
        if data.get('categoryId'):
            try:
                category = FAQCategory.objects.get(pk=data['categoryId'])
            except FAQCategory.DoesNotExist:
                pass

        faq = FAQ.objects.create(
            question=question,
            answer=answer,
            category=category,
            order=int(data.get('order', 0)),
            is_active=str(data.get('isActive', 'true')).lower() != 'false',
        )
        return Response(_serialize_faq(faq), status=201)


class AdminFAQDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get(self, pk):
        try:
            return FAQ.objects.select_related('category').get(pk=pk)
        except FAQ.DoesNotExist:
            return None

    def patch(self, request, pk):
        faq = self._get(pk)
        if not faq:
            return Response({'error': {'message': 'سوال یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        data = request.data
        update_fields = []
        for key in ['question', 'answer']:
            if key in data:
                setattr(faq, key, data[key])
                update_fields.append(key)
        if 'order' in data:
            faq.order = int(data['order'])
            update_fields.append('order')
        if 'isActive' in data:
            faq.is_active = str(data['isActive']).lower() not in ('false', '0')
            update_fields.append('is_active')
        if 'categoryId' in data:
            try:
                faq.category = FAQCategory.objects.get(pk=data['categoryId'])
                update_fields.append('category')
            except FAQCategory.DoesNotExist:
                pass
        if update_fields:
            faq.save(update_fields=update_fields)
        faq.refresh_from_db()
        return Response(_serialize_faq(faq))

    def delete(self, request, pk):
        faq = self._get(pk)
        if not faq:
            return Response({'error': {'message': 'سوال یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        faq.delete()
        return Response(status=204)


class AdminFAQReorderView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        items = request.data.get('items', [])
        updated = 0
        for item in items:
            count = FAQ.objects.filter(pk=item['id']).update(order=item['order'])
            updated += count
        return Response({'updated': updated})
