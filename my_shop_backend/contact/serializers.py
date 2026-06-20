import re
from rest_framework import serializers

IMAGE_MIMES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
VIDEO_MIMES = {'video/mp4', 'video/quicktime', 'video/x-msvideo'}

MAX_IMAGE_SIZE = 1 * 1024 * 1024   # 1 MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_IMAGES = 5
MAX_VIDEOS = 1


class ContactSubmitSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=300)
    orderNumber = serializers.CharField(max_length=50, required=False, allow_blank=True)
    fullName = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    message = serializers.CharField(required=False, allow_blank=True)

    def validate_phone(self, value):
        if not re.match(r'^09\d{9}$', value.strip()):
            raise serializers.ValidationError("شماره تماس باید ۱۱ رقم باشد")
        return value.strip()

    def validate_subject(self, value):
        if not value.strip():
            raise serializers.ValidationError("موضوع الزامی است")
        return value.strip()
