import math
import uuid
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from core.responses import success_response, error_response
from .models import FAQCategory, FAQ, UserQuestion


def _faq_data(faq):
    return {
        'id': str(faq.id),
        'question': faq.question,
        'answer': faq.answer,
        'categoryId': str(faq.category_id) if faq.category_id else None,
        'categoryName': faq.category.name if faq.category else None,
    }


def _paginate(qs, page, limit):
    total = qs.count()
    offset = (page - 1) * limit
    items = list(qs[offset: offset + limit])
    total_pages = math.ceil(total / limit) if total else 1
    return items, total, {'page': page, 'limit': limit, 'totalPages': total_pages}


# ---------------------------------------------------------------------------
# 1. GET /faq/categories/
# ---------------------------------------------------------------------------
class FAQCategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = FAQCategory.objects.all()
        data = [
            {
                'id': cat.id,
                'name': cat.name,
                'icon': cat.icon,
                'questionCount': cat.question_count,
            }
            for cat in categories
        ]
        return success_response({'categories': data})


# ---------------------------------------------------------------------------
# 2. GET /faq/
# ---------------------------------------------------------------------------
class FAQListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = FAQ.objects.filter(is_active=True).select_related('category')

        category_id = request.query_params.get('categoryId', '').strip()
        if category_id:
            try:
                qs = qs.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                return error_response("categoryId نامعتبر است", status=400)

        q = request.query_params.get('q', '').strip()
        if q:
            qs = qs.filter(question__icontains=q) | qs.filter(answer__icontains=q)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1
        try:
            limit = max(1, min(100, int(request.query_params.get('limit', 20))))
        except (ValueError, TypeError):
            limit = 20

        items, total, pagination = _paginate(qs.distinct(), page, limit)
        return success_response({
            'faqs': [_faq_data(f) for f in items],
            'total': total,
            'pagination': pagination,
        })


# ---------------------------------------------------------------------------
# 3. GET /faq/search/
# ---------------------------------------------------------------------------
class FAQSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return error_response("پارامتر q الزامی است", status=400)

        try:
            limit = max(1, min(100, int(request.query_params.get('limit', 20))))
        except (ValueError, TypeError):
            limit = 20

        qs = FAQ.objects.filter(is_active=True).select_related('category')
        qs = (qs.filter(question__icontains=q) | qs.filter(answer__icontains=q)).distinct()[:limit]
        faqs = list(qs)

        return success_response({
            'faqs': [_faq_data(f) for f in faqs],
            'total': len(faqs),
            'query': q,
        })


# ---------------------------------------------------------------------------
# 4. GET /faq/{faqId}/
# ---------------------------------------------------------------------------
class FAQDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, faq_id):
        try:
            faq = FAQ.objects.select_related('category').get(pk=faq_id, is_active=True)
        except FAQ.DoesNotExist:
            return error_response("سوال یافت نشد", status=404)

        related = FAQ.objects.filter(
            category=faq.category, is_active=True
        ).exclude(pk=faq.pk)[:4]

        data = {
            **_faq_data(faq),
            'relatedFaqs': [
                {'id': str(r.id), 'question': r.question}
                for r in related
            ],
        }
        return success_response(data)


# ---------------------------------------------------------------------------
# 5. POST /faq/{faqId}/helpful/
# ---------------------------------------------------------------------------
class FAQHelpfulView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, faq_id):
        try:
            faq = FAQ.objects.get(pk=faq_id, is_active=True)
        except FAQ.DoesNotExist:
            return error_response("سوال یافت نشد", status=404)

        helpful = request.data.get('helpful')
        if helpful is None:
            return error_response("فیلد helpful الزامی است", status=400)

        if helpful is True or helpful == 'true' or helpful == 1:
            faq.helpful_count += 1
        else:
            faq.not_helpful_count += 1
        faq.save(update_fields=['helpful_count', 'not_helpful_count'])

        return success_response({
            'helpfulCount': faq.helpful_count,
            'notHelpfulCount': faq.not_helpful_count,
        })


# ---------------------------------------------------------------------------
# 6. POST /faq/ask/
# ---------------------------------------------------------------------------
class FAQAskView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        question_text = request.data.get('question', '').strip()
        if not question_text:
            return error_response("متن سوال الزامی است", status=400)

        email = request.data.get('email', '').strip()
        category_id = request.data.get('categoryId')

        category = None
        if category_id:
            try:
                category = FAQCategory.objects.get(pk=int(category_id))
            except (FAQCategory.DoesNotExist, ValueError, TypeError):
                pass

        count = UserQuestion.objects.count() + 1
        question_id = f"user_q_{count:03d}"

        UserQuestion.objects.create(
            question_id=question_id,
            question=question_text,
            category=category,
            email=email,
        )

        return Response({
            'success': True,
            'message': 'سوال شما دریافت شد. پس از بررسی، پاسخ به ایمیل شما ارسال می‌شود.',
            'data': {'questionId': question_id},
        }, status=201)
