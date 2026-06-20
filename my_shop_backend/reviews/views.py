import math
from django.db.models import Avg, Count, Case, When, IntegerField
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from core.responses import data_response, error_detail_response
from products.models import Product
from .models import Comment, CommentVote, Question, Answer, AnswerVote
from .serializers import (
    CommentSerializer, CommentCreateSerializer,
    QuestionSerializer, QuestionCreateSerializer,
    AnswerSerializer, AnswerCreateSerializer,
)


def _parse_page_params(query_params, default_limit=10):
    try:
        page = max(1, int(query_params.get('page', 1)))
    except (ValueError, TypeError):
        page = 1
    try:
        limit = max(1, min(100, int(query_params.get('limit', default_limit))))
    except (ValueError, TypeError):
        limit = default_limit
    return page, limit


def _paginate(qs, page, limit):
    total = qs.count()
    total_pages = math.ceil(total / limit) if total else 1
    items = list(qs[(page - 1) * limit: page * limit])
    return items, total, {
        'currentPage': page,
        'totalPages': total_pages,
        'hasNext': page < total_pages,
    }


# ---------------------------------------------------------------------------
# 3. GET /products/:id/comments
# 4. POST /products/:id/comments
# ---------------------------------------------------------------------------
class CommentsView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, product_id):
        if not Product.objects.filter(pk=product_id).exists():
            return error_detail_response('NOT_FOUND', "محصول یافت نشد", http_status=404)

        qs = (
            Comment.objects
            .filter(product_id=product_id)
            .prefetch_related('images', 'votes')
            .select_related('user')
        )

        sort = request.query_params.get('sort', 'newest')
        if sort == 'top_rated':
            qs = qs.order_by('-star', '-created_at')
        elif sort == 'has_image':
            qs = qs.filter(images__isnull=False).distinct().order_by('-created_at')
        else:
            qs = qs.order_by('-created_at')

        page, limit = _parse_page_params(request.query_params)
        items, total, pagination = _paginate(qs, page, limit)
        pagination['totalCount'] = total

        # Summary always computed over all comments (ignoring sort/filter)
        agg = Comment.objects.filter(product_id=product_id).aggregate(
            avg=Avg('star'),
            total=Count('id'),
            s1=Count(Case(When(star=1, then=1), output_field=IntegerField())),
            s2=Count(Case(When(star=2, then=1), output_field=IntegerField())),
            s3=Count(Case(When(star=3, then=1), output_field=IntegerField())),
            s4=Count(Case(When(star=4, then=1), output_field=IntegerField())),
            s5=Count(Case(When(star=5, then=1), output_field=IntegerField())),
        )

        serializer = CommentSerializer(items, many=True, context={'request': request})
        return data_response({
            'summary': {
                'averageRating': round(float(agg['avg'] or 0), 1),
                'totalCount': agg['total'],
                'distribution': {
                    '5': agg['s5'],
                    '4': agg['s4'],
                    '3': agg['s3'],
                    '2': agg['s2'],
                    '1': agg['s1'],
                },
            },
            'pagination': pagination,
            'items': serializer.data,
        })

    def post(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return error_detail_response('NOT_FOUND', "محصول یافت نشد", http_status=404)

        if Comment.objects.filter(product=product, user=request.user).exists():
            return error_detail_response('CONFLICT', "شما قبلاً برای این محصول نظر ثبت کرده‌اید", http_status=409)

        serializer = CommentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            first_field = next(iter(serializer.errors))
            msg = str(serializer.errors[first_field][0])
            return error_detail_response('VALIDATION_ERROR', msg, field=first_field, http_status=400)

        comment = serializer.save(product=product, user=request.user)
        out = CommentSerializer(comment, context={'request': request})
        return data_response(out.data, message="نظر شما با موفقیت ثبت شد", status=201)


# ---------------------------------------------------------------------------
# 5. POST /comments/:id/helpful
# ---------------------------------------------------------------------------
class CommentHelpfulView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            comment = Comment.objects.prefetch_related('votes').get(pk=pk)
        except Comment.DoesNotExist:
            return error_detail_response('NOT_FOUND', "نظر یافت نشد", http_status=404)

        vote_type = request.data.get('type')
        if vote_type not in (CommentVote.LIKE, CommentVote.DISLIKE):
            return error_detail_response(
                'VALIDATION_ERROR', "مقدار type باید like یا dislike باشد",
                field="type", http_status=400
            )

        vote, created = CommentVote.objects.get_or_create(
            comment=comment, user=request.user,
            defaults={'vote_type': vote_type}
        )
        if not created:
            if vote.vote_type == vote_type:
                vote.delete()
                user_vote = None
            else:
                vote.vote_type = vote_type
                vote.save()
                user_vote = vote_type
        else:
            user_vote = vote_type

        likes = comment.votes.filter(vote_type=CommentVote.LIKE).count()
        dislikes = comment.votes.filter(vote_type=CommentVote.DISLIKE).count()
        return data_response({'likes': likes, 'dislikes': dislikes, 'userVote': user_vote})


# ---------------------------------------------------------------------------
# 6. GET /products/:id/questions
# 7. POST /products/:id/questions
# ---------------------------------------------------------------------------
class QuestionsView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, product_id):
        if not Product.objects.filter(pk=product_id).exists():
            return error_detail_response('NOT_FOUND', "محصول یافت نشد", http_status=404)

        qs = (
            Question.objects
            .filter(product_id=product_id)
            .prefetch_related('answers__votes', 'answers__user')
        )

        sort = request.query_params.get('sort', 'newest')
        if sort == 'most_answers':
            qs = qs.annotate(ans_count=Count('answers')).order_by('-ans_count', '-created_at')
        else:
            qs = qs.order_by('-created_at')

        page, limit = _parse_page_params(request.query_params)
        items, total, pagination = _paginate(qs, page, limit)

        serializer = QuestionSerializer(items, many=True, context={'request': request})
        return data_response({
            'totalCount': total,
            'pagination': pagination,
            'items': serializer.data,
        })

    def post(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return error_detail_response('NOT_FOUND', "محصول یافت نشد", http_status=404)

        serializer = QuestionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            first_field = next(iter(serializer.errors))
            msg = str(serializer.errors[first_field][0])
            return error_detail_response('VALIDATION_ERROR', msg, field=first_field, http_status=400)

        question = serializer.save(product=product, user=request.user)
        out = QuestionSerializer(question, context={'request': request})
        return data_response(out.data, message="سوال شما با موفقیت ثبت شد", status=201)


# ---------------------------------------------------------------------------
# 8. POST /questions/:id/answers
# ---------------------------------------------------------------------------
class AnswersView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return error_detail_response('NOT_FOUND', "سوال یافت نشد", http_status=404)

        serializer = AnswerCreateSerializer(data=request.data)
        if not serializer.is_valid():
            first_field = next(iter(serializer.errors))
            msg = str(serializer.errors[first_field][0])
            return error_detail_response('VALIDATION_ERROR', msg, field=first_field, http_status=400)

        answer = serializer.save(question=question, user=request.user)
        out = AnswerSerializer(answer, context={'request': request})
        return data_response(out.data, message="پاسخ شما با موفقیت ثبت شد", status=201)


# ---------------------------------------------------------------------------
# 9. POST /answers/:id/helpful
# ---------------------------------------------------------------------------
class AnswerHelpfulView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            answer = Answer.objects.prefetch_related('votes').get(pk=pk)
        except Answer.DoesNotExist:
            return error_detail_response('NOT_FOUND', "پاسخ یافت نشد", http_status=404)

        vote_type = request.data.get('type')
        if vote_type not in (AnswerVote.LIKE, AnswerVote.DISLIKE):
            return error_detail_response(
                'VALIDATION_ERROR', "مقدار type باید like یا dislike باشد",
                field="type", http_status=400
            )

        vote, created = AnswerVote.objects.get_or_create(
            answer=answer, user=request.user,
            defaults={'vote_type': vote_type}
        )
        if not created:
            if vote.vote_type == vote_type:
                vote.delete()
                user_vote = None
            else:
                vote.vote_type = vote_type
                vote.save()
                user_vote = vote_type
        else:
            user_vote = vote_type

        likes = answer.votes.filter(vote_type=AnswerVote.LIKE).count()
        dislikes = answer.votes.filter(vote_type=AnswerVote.DISLIKE).count()
        return data_response({'likes': likes, 'dislikes': dislikes, 'userVote': user_vote})
