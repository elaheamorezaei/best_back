from django.db import models


class BlogCategory(models.Model):
    slug = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=1000, blank=True)
    excerpt = models.CharField(max_length=500, blank=True)
    content = models.TextField(blank=True)
    slug = models.SlugField(max_length=300, unique=True, allow_unicode=True)
    image = models.ImageField(upload_to='blog/posts/')
    category = models.ForeignKey(
        BlogCategory, related_name='posts',
        null=True, blank=True, on_delete=models.SET_NULL,
    )
    views = models.PositiveIntegerField(default=0)
    read_time = models.CharField(max_length=50, blank=True)
    tags = models.JSONField(default=list, blank=True)
    author_name = models.CharField(max_length=200, default='تیم بست')
    author_avatar = models.ImageField(upload_to='blog/authors/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class BlogBanner(models.Model):
    image = models.ImageField(upload_to='blog/banners/')
    alt = models.CharField(max_length=200)
    href = models.CharField(max_length=500)
    position = models.CharField(max_length=50, default='top')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.alt} ({self.position})"


class BlogMagazineItem(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=300, unique=True, allow_unicode=True)
    image = models.ImageField(upload_to='blog/magazine/')
    video = models.FileField(upload_to='blog/videos/', null=True, blank=True)
    video_mime_type = models.CharField(max_length=50, default='video/mp4')
    thumbnail = models.ImageField(upload_to='blog/thumbnails/', null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    read_time = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
