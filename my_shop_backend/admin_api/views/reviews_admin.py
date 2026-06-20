from rest_framework.views import APIView
from rest_framework.response import Response

from admin_api.permissions import IsAdminUser
from reviews.models import Comment
from core.responses import build_absolute_image_url
from orders.models import Order


def _is_verified(comment):
    return Order.objects.filter(
        user=comment.user,
        items__product=comment.product,
        status__in=[Order.STATUS_DELIVERED, Order.STATUS_PROCESSING, Order.STATUS_SHIPPED]
    ).exists()


def _serialize_comment(comment, request=None):
    profile = getattr(comment.user, 'profile', None)
    return {
        'id': comment.id,
        'productId': comment.product_id,
        'productName': comment.product.name,
        'userId': comment.user_id,
        'userName': profile.full_name if profile else comment.user.username,
        'rating': comment.star,
        'title': comment.title,
        'comment': comment.text,
        'pros': comment.pros or [],
        'cons': comment.cons or [],
        'isApproved': comment.is_approved,
        'isVerified': _is_verified(comment),
        'helpfulCount': comment.votes.filter(vote_type='like').count(),
        'createdAt': comment.created_at.isoformat(),
    }


class AdminReviewListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = Comment.objects.select_related('product', 'user__profile').prefetch_related('votes')

        if request.query_params.get('isApproved') == 'true':
            qs = qs.filter(is_approved=True)
        elif request.query_params.get('isApproved') == 'false':
            qs = qs.filter(is_approved=False)

        product_id = request.query_params.get('productId')
        if product_id:
            qs = qs.filter(product_id=product_id)

        rating = request.query_params.get('rating')
        if rating:
            qs = qs.filter(star=rating)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = max(1, min(100, int(request.query_params.get('pageSize', 20))))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        total = qs.count()
        start = (page - 1) * page_size
        items = list(qs[start:start + page_size])

        return Response({
            'results': [_serialize_comment(c, request) for c in items],
            'count': total,
            'next': None,
            'previous': None,
        })


class AdminReviewDetailView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({'error': {'message': 'نظر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        comment.delete()
        return Response(status=204)


class AdminReviewApproveView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({'error': {'message': 'نظر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        comment.is_approved = True
        comment.save(update_fields=['is_approved'])
        return Response({'isApproved': True})


class AdminReviewRejectView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({'error': {'message': 'نظر یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        comment.is_approved = False
        comment.save(update_fields=['is_approved'])
        return Response({'isApproved': False})


class AdminReviewBulkApproveView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': {'message': 'ids الزامی است', 'code': 'MISSING_IDS'}}, status=400)
        approved = Comment.objects.filter(pk__in=ids).update(is_approved=True)
        return Response({'approved': approved})
