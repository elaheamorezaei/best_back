from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from core.responses import success_response, error_response
from .models import BlogCategory, BlogPost, BlogBanner, BlogMagazineItem
from .serializers import (
    BlogCategorySerializer, BlogPostListSerializer, BlogPostDetailSerializer,
    BlogPopularPostSerializer, BlogBannerSerializer, BlogMagazineItemSerializer,
    BlogSearchResultSerializer,
)


def _paginate(queryset, page, limit):
    total = queryset.count()
    offset = (page - 1) * limit
    items = queryset[offset: offset + limit]
    import math
    total_pages = math.ceil(total / limit) if total else 1
    return items, total, {'page': page, 'limit': limit, 'totalPages': total_pages}


class BlogCategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = BlogCategory.objects.prefetch_related('posts')
        serializer = BlogCategorySerializer(categories, many=True)
        return success_response({'categories': serializer.data})


class BlogPostListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = BlogPost.objects.filter(is_active=True).select_related('category')

        category = request.query_params.get('category', '').strip()
        if category and category not in ('all', 'new'):
            qs = qs.filter(category__slug=category)

        q = request.query_params.get('q', '').strip()
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(subtitle__icontains=q)

        sort = request.query_params.get('sort', 'newest')
        if sort == 'popular':
            qs = qs.order_by('-views', '-created_at')
        elif sort == 'most_viewed':
            qs = qs.order_by('-views')
        else:
            qs = qs.order_by('-created_at')

        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1
        try:
            limit = max(1, min(50, int(request.query_params.get('limit', 9))))
        except (ValueError, TypeError):
            limit = 9

        items, total, pagination = _paginate(qs, page, limit)
        serializer = BlogPostListSerializer(items, many=True, context={'request': request})
        return success_response({
            'posts': serializer.data,
            'total': total,
            'pagination': pagination,
        })


class BlogPostDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, post_id):
        try:
            post = BlogPost.objects.select_related('category').prefetch_related(
                'category__posts'
            ).get(pk=post_id, is_active=True)
        except BlogPost.DoesNotExist:
            return error_response("مطلب یافت نشد", status=404)
        serializer = BlogPostDetailSerializer(post, context={'request': request})
        return success_response(serializer.data)


class BlogPostViewIncrementView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, post_id):
        try:
            post = BlogPost.objects.get(pk=post_id, is_active=True)
        except BlogPost.DoesNotExist:
            # Also try magazine items
            try:
                item = BlogMagazineItem.objects.get(pk=post_id, is_active=True)
                item.views += 1
                item.save(update_fields=['views'])
                return success_response({'views': item.views})
            except BlogMagazineItem.DoesNotExist:
                return error_response("مطلب یافت نشد", status=404)
        post.views += 1
        post.save(update_fields=['views'])
        return success_response({'views': post.views})


class BlogBannerListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        banners = BlogBanner.objects.filter(is_active=True)
        serializer = BlogBannerSerializer(banners, many=True, context={'request': request})
        return success_response({'banners': serializer.data})


class BlogPopularPostsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            limit = max(1, min(20, int(request.query_params.get('limit', 4))))
        except (ValueError, TypeError):
            limit = 4
        posts = BlogPost.objects.filter(is_active=True).order_by('-views')[:limit]
        serializer = BlogPopularPostSerializer(posts, many=True, context={'request': request})
        return success_response({'posts': serializer.data})


class BlogMagazineView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1
        try:
            limit = max(1, min(20, int(request.query_params.get('limit', 4))))
        except (ValueError, TypeError):
            limit = 4

        qs = BlogMagazineItem.objects.filter(is_active=True)
        items, total, pagination = _paginate(qs, page, limit)
        serializer = BlogMagazineItemSerializer(items, many=True, context={'request': request})
        return success_response({
            'items': serializer.data,
            'total': total,
            'pagination': pagination,
        })


class BlogSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return error_response("پارامتر q الزامی است", status=400)

        qs = BlogPost.objects.filter(is_active=True).select_related('category')
        qs = qs.filter(title__icontains=q) | qs.filter(subtitle__icontains=q) | qs.filter(content__icontains=q)

        category = request.query_params.get('category', '').strip()
        if category:
            qs = qs.filter(category__slug=category)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1

        limit = 9
        items, total, pagination = _paginate(qs.order_by('-created_at').distinct(), page, limit)
        serializer = BlogSearchResultSerializer(items, many=True, context={'request': request})
        return success_response({
            'posts': serializer.data,
            'total': total,
            'pagination': {
                'page': pagination['page'],
                'totalPages': pagination['totalPages'],
            },
        })
