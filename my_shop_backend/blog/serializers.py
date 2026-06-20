from rest_framework import serializers
from core.responses import build_absolute_image_url
from core.utils import to_persian_date
from .models import BlogCategory, BlogPost, BlogBanner, BlogMagazineItem


class BlogCategorySerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='slug')
    postCount = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'icon', 'postCount']

    def get_postCount(self, obj):
        return obj.posts.filter(is_active=True).count()


class BlogPostListSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.slug', default=None)
    categoryName = serializers.CharField(source='category.name', default=None)
    readTime = serializers.CharField(source='read_time')

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'subtitle', 'date', 'image',
            'category', 'categoryName', 'views', 'readTime', 'slug',
        ]

    def get_date(self, obj):
        return to_persian_date(obj.created_at)

    def get_image(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)


class BlogPostDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.slug', default=None)
    categoryName = serializers.CharField(source='category.name', default=None)
    readTime = serializers.CharField(source='read_time')
    author = serializers.SerializerMethodField()
    relatedPosts = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'subtitle', 'content', 'date', 'image',
            'category', 'categoryName', 'views', 'readTime', 'slug',
            'tags', 'author', 'relatedPosts',
        ]

    def get_date(self, obj):
        return to_persian_date(obj.created_at)

    def get_image(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)

    def get_author(self, obj):
        return {
            'name': obj.author_name,
            'avatar': build_absolute_image_url(self.context.get('request'), obj.author_avatar),
        }

    def get_relatedPosts(self, obj):
        request = self.context.get('request')
        related = BlogPost.objects.filter(
            category=obj.category, is_active=True
        ).exclude(pk=obj.pk)[:4]
        return [
            {
                'id': str(p.id),
                'title': p.title,
                'image': build_absolute_image_url(request, p.image),
                'date': to_persian_date(p.created_at),
            }
            for p in related
        ]


class BlogPopularPostSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    image = serializers.SerializerMethodField()
    readTime = serializers.CharField(source='read_time')

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'readTime', 'views', 'image', 'slug']

    def get_image(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)


class BlogBannerSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = BlogBanner
        fields = ['id', 'src', 'alt', 'href', 'position']

    def get_src(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)


class BlogMagazineItemSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    videoUrl = serializers.SerializerMethodField()
    videoMimeType = serializers.CharField(source='video_mime_type')
    thumbnailUrl = serializers.SerializerMethodField()
    readTime = serializers.CharField(source='read_time')

    class Meta:
        model = BlogMagazineItem
        fields = [
            'id', 'title', 'description', 'date', 'readTime',
            'views', 'image', 'videoUrl', 'videoMimeType', 'thumbnailUrl', 'slug',
        ]

    def get_date(self, obj):
        return to_persian_date(obj.created_at)

    def get_image(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)

    def get_videoUrl(self, obj):
        if not obj.video:
            return None
        request = self.context.get('request')
        try:
            url = obj.video.url
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None

    def get_thumbnailUrl(self, obj):
        field = obj.thumbnail if obj.thumbnail else obj.image
        return build_absolute_image_url(self.context.get('request'), field)


class BlogSearchResultSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    date = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    category = serializers.CharField(source='category.slug', default=None)

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'subtitle', 'date', 'image', 'category', 'slug']

    def get_date(self, obj):
        return to_persian_date(obj.created_at)

    def get_image(self, obj):
        return build_absolute_image_url(self.context.get('request'), obj.image)
