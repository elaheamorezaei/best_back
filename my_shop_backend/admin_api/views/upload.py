import os
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from admin_api.permissions import IsAdminUser


ALLOWED_FOLDERS = {'products', 'blog', 'banners', 'sliders', 'settings'}
MAX_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}


class AdminUploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        folder = request.data.get('folder', 'products').strip()

        if not file:
            return Response({'error': {'message': 'فایل الزامی است', 'code': 'MISSING_FILE'}}, status=400)

        if folder not in ALLOWED_FOLDERS:
            folder = 'products'

        if file.size > MAX_SIZE:
            return Response({'error': {'message': 'حجم فایل نباید بیشتر از ۵ مگابایت باشد', 'code': 'FILE_TOO_LARGE'}}, status=400)

        if file.content_type not in ALLOWED_TYPES:
            return Response({'error': {'message': 'فرمت فایل باید JPG، PNG، WebP یا GIF باشد', 'code': 'INVALID_FORMAT'}}, status=400)

        ext = os.path.splitext(file.name)[1].lower() or '.jpg'
        filename = f'{uuid.uuid4().hex}{ext}'
        relative_path = os.path.join(folder, filename)
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)

        url = request.build_absolute_uri(settings.MEDIA_URL + relative_path.replace('\\', '/'))
        return Response({
            'url': url,
            'width': None,
            'height': None,
            'size': file.size,
        })
