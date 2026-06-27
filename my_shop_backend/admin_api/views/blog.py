from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from admin_api.permissions import IsAdminUser
from blog.models import BlogPost, BlogCategory
from core.responses import build_absolute_image_url


def _serialize_post(post, request):
    return {
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'excerpt': post.excerpt,
        'content': post.content,
        'coverImage': build_absolute_image_url(request, post.image),
        'categoryId': post.category_id,
        'categoryName': post.category.name if post.category else None,
        'tags': post.tags or [],
        'isPublished': post.is_published,
        'isFeatured': post.is_featured,
        'viewCount': post.views,
        'publishedAt': post.published_at.isoformat() if post.published_at else None,
        'createdAt': post.created_at.isoformat(),
    }


class AdminBlogListView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = BlogPost.objects.select_related('category')

        if request.query_params.get('isPublished') == 'true':
            qs = qs.filter(is_published=True)
        elif request.query_params.get('isPublished') == 'false':
            qs = qs.filter(is_published=False)

        if request.query_params.get('isFeatured') == 'true':
            qs = qs.filter(is_featured=True)

        category_id = request.query_params.get('categoryId')
        if category_id:
            try:
                qs = qs.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                pass

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(title__icontains=search)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = max(1, min(100, int(request.query_params.get('pageSize', 20))))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        total = qs.count()
        start = (page - 1) * page_size
        items = list(qs[start:start + page_size])

        return Response({
            'results': [_serialize_post(p, request) for p in items],
            'count': total,
            'next': None,
            'previous': None,
        })

    def post(self, request):
        data = request.data
        title = data.get('title', '').strip()
        slug = data.get('slug', '').strip()
        content = data.get('content', '').strip()

        if not title or not slug or not content:
            return Response({'error': {'message': 'عنوان، slug و محتوا الزامی است', 'code': 'MISSING_FIELDS'}}, status=400)

        if BlogPost.objects.filter(slug=slug).exists():
            return Response({'error': {'message': 'slug تکراری است', 'code': 'DUPLICATE_SLUG'}}, status=409)

        post = BlogPost(
            title=title,
            slug=slug,
            excerpt=data.get('excerpt', ''),
            content=content,
            is_published=str(data.get('isPublished', 'false')).lower() == 'true',
            is_featured=str(data.get('isFeatured', 'false')).lower() == 'true',
        )

        if post.is_published:
            post.published_at = timezone.now()

        category_id = data.get('categoryId')
        if category_id:
            try:
                post.category = BlogCategory.objects.get(pk=category_id)
            except (BlogCategory.DoesNotExist, ValueError, TypeError):
                pass

        import json
        tags = data.get('tags', '[]')
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except Exception:
                tags = []
        post.tags = tags

        if 'image' not in request.FILES:
            return Response({'error': {'message': 'تصویر مقاله الزامی است', 'code': 'MISSING_IMAGE'}}, status=400)
        post.image = request.FILES['image']
        post.save()

        return Response(_serialize_post(post, request), status=201)


class AdminBlogDetailView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get(self, pk):
        try:
            return BlogPost.objects.select_related('category').get(pk=pk)
        except BlogPost.DoesNotExist:
            return None

    def get(self, request, pk):
        post = self._get(pk)
        if not post:
            return Response({'error': {'message': 'مقاله یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        return Response(_serialize_post(post, request))

    def patch(self, request, pk):
        post = self._get(pk)
        if not post:
            return Response({'error': {'message': 'مقاله یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        data = request.data
        update_fields = []

        for api_key, model_field in [('title', 'title'), ('slug', 'slug'), ('excerpt', 'excerpt'), ('content', 'content')]:
            if api_key in data:
                if api_key == 'slug' and BlogPost.objects.filter(slug=data[api_key]).exclude(pk=pk).exists():
                    return Response({'error': {'message': 'slug تکراری است', 'code': 'DUPLICATE_SLUG'}}, status=409)
                setattr(post, model_field, data[api_key])
                update_fields.append(model_field)

        for api_key, model_field in [('isPublished', 'is_published'), ('isFeatured', 'is_featured')]:
            if api_key in data:
                val = str(data[api_key]).lower() not in ('false', '0')
                setattr(post, model_field, val)
                update_fields.append(model_field)
                if model_field == 'is_published' and val and not post.published_at:
                    post.published_at = timezone.now()
                    update_fields.append('published_at')

        if 'categoryId' in data:
            cid = data['categoryId']
            if cid:
                try:
                    post.category = BlogCategory.objects.get(pk=cid)
                    update_fields.append('category')
                except (BlogCategory.DoesNotExist, ValueError, TypeError):
                    pass

        if 'image' in request.FILES:
            post.image = request.FILES['image']
            update_fields.append('image')

        if update_fields:
            post.save(update_fields=update_fields)

        post.refresh_from_db()
        return Response(_serialize_post(post, request))

    def delete(self, request, pk):
        post = self._get(pk)
        if not post:
            return Response({'error': {'message': 'مقاله یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        post.delete()
        return Response(status=204)


class AdminBlogTogglePublishView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            post = BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            return Response({'error': {'message': 'مقاله یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        post.is_published = not post.is_published
        update_fields = ['is_published']
        if post.is_published and not post.published_at:
            post.published_at = timezone.now()
            update_fields.append('published_at')
        post.save(update_fields=update_fields)

        return Response({
            'isPublished': post.is_published,
            'publishedAt': post.published_at.isoformat() if post.published_at else None,
        })
