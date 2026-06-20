import uuid
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from core.responses import success_response, error_response, build_absolute_image_url
from .models import (
    ContactInfo, ContactSlider, ContactSubject,
    ContactTicket, ContactTicketAttachment, ContactTicketResponse,
)
from .serializers import (
    ContactSubmitSerializer,
    IMAGE_MIMES, VIDEO_MIMES,
    MAX_IMAGE_SIZE, MAX_VIDEO_SIZE, MAX_IMAGES, MAX_VIDEOS,
)


def _generate_ticket_id():
    count = ContactTicket.objects.count() + 1
    return f"TKT-{count:06d}"


def _validate_files(files):
    """Validate uploaded files. Returns (images, videos, error_response_or_None)."""
    images, videos = [], []
    for f in files:
        mime = getattr(f, 'content_type', '')
        if mime in IMAGE_MIMES:
            images.append(f)
        elif mime in VIDEO_MIMES:
            videos.append(f)
        else:
            return [], [], Response({
                'success': False,
                'message': 'نوع فایل پشتیبانی نمی‌شود. فقط تصویر و ویدیو مجاز است.',
                'errors': {'files': 'نوع فایل نامعتبر است'},
            }, status=422)

    if len(images) > MAX_IMAGES or len(videos) > MAX_VIDEOS:
        return [], [], Response({
            'success': False,
            'message': 'حجم فایل‌های ارسالی از حد مجاز بیشتر است',
            'data': {'maxImageSize': '1MB', 'maxVideoSize': '50MB', 'maxFiles': MAX_IMAGES + MAX_VIDEOS},
        }, status=413)

    for img in images:
        if img.size > MAX_IMAGE_SIZE:
            return [], [], Response({
                'success': False,
                'message': 'حجم فایل‌های ارسالی از حد مجاز بیشتر است',
                'data': {'maxImageSize': '1MB', 'maxVideoSize': '50MB', 'maxFiles': MAX_IMAGES + MAX_VIDEOS},
            }, status=413)

    for vid in videos:
        if vid.size > MAX_VIDEO_SIZE:
            return [], [], Response({
                'success': False,
                'message': 'حجم فایل‌های ارسالی از حد مجاز بیشتر است',
                'data': {'maxImageSize': '1MB', 'maxVideoSize': '50MB', 'maxFiles': MAX_IMAGES + MAX_VIDEOS},
            }, status=413)

    return images, videos, None


# ---------------------------------------------------------------------------
# 1. POST /contact/submit/
# ---------------------------------------------------------------------------
class ContactSubmitView(APIView):
    permission_classes = [AllowAny]
    parser_classes_override = None  # Uses default (multipart + json)

    def post(self, request):
        serializer = ContactSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            errors = {
                k: str(v[0]) if isinstance(v, list) else str(v)
                for k, v in serializer.errors.items()
            }
            return Response({
                'success': False,
                'message': 'خطای اعتبارسنجی',
                'errors': errors,
            }, status=422)

        data = serializer.validated_data
        files = request.FILES.getlist('files')

        images, videos, file_error = _validate_files(files)
        if file_error:
            return file_error

        user = request.user if request.user.is_authenticated else None
        ticket = ContactTicket.objects.create(
            ticket_id=_generate_ticket_id(),
            subject=data['subject'],
            order_number=data.get('orderNumber', ''),
            full_name=data['fullName'],
            email=data['email'],
            phone=data['phone'],
            message=data.get('message', ''),
            user=user,
        )

        for img in images:
            ContactTicketAttachment.objects.create(
                ticket=ticket,
                file=img,
                file_type=ContactTicketAttachment.TYPE_IMAGE,
            )
        for vid in videos:
            ContactTicketAttachment.objects.create(
                ticket=ticket,
                file=vid,
                file_type=ContactTicketAttachment.TYPE_VIDEO,
            )

        return Response({
            'success': True,
            'message': 'پیام شما با موفقیت ارسال شد. تیم پشتیبانی ظرف ۱ تا ۲ روز کاری پاسخ می‌دهد.',
            'data': {
                'ticketId': ticket.ticket_id,
                'estimatedResponseTime': '1-2 روز کاری',
            },
        })


# ---------------------------------------------------------------------------
# 2. GET /contact/info/
# ---------------------------------------------------------------------------
class ContactInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        info = ContactInfo.objects.first()
        if not info:
            return success_response({
                'hero': {'text': ''},
                'map': {'title': '', 'subtitle': '', 'iframeSrc': '', 'coordinates': {'lat': 35.7, 'lng': 51.4}},
                'support': {'phones': [], 'mainPhone': '', 'email': '', 'workingHours': ''},
                'address': '',
            })
        return success_response({
            'hero': {'text': info.hero_text},
            'map': {
                'title': info.map_title,
                'subtitle': info.map_subtitle,
                'iframeSrc': info.map_iframe_src,
                'coordinates': {'lat': info.map_lat, 'lng': info.map_lng},
            },
            'support': {
                'phones': info.support_phones,
                'mainPhone': info.main_phone,
                'email': info.support_email,
                'workingHours': info.working_hours,
            },
            'address': info.address,
        })


# ---------------------------------------------------------------------------
# 3. GET /contact/slider/
# ---------------------------------------------------------------------------
class ContactSliderView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        slider = ContactSlider.objects.first()
        if not slider:
            return success_response({'slider': None})
        return success_response({
            'slider': {
                'src': build_absolute_image_url(request, slider.image),
                'alt': slider.alt,
            }
        })


# ---------------------------------------------------------------------------
# 4. GET /contact/subjects/
# ---------------------------------------------------------------------------
class ContactSubjectsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        subjects = ContactSubject.objects.all()
        return success_response({
            'subjects': [{'id': s.id, 'label': s.label} for s in subjects]
        })


# ---------------------------------------------------------------------------
# 5. GET /contact/tickets/{ticketId}/
# ---------------------------------------------------------------------------
class ContactTicketDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, ticket_id):
        try:
            ticket = ContactTicket.objects.prefetch_related('responses').get(
                ticket_id=ticket_id
            )
        except ContactTicket.DoesNotExist:
            return error_response("تیکت یافت نشد", status=404)

        responses_data = [
            {
                'id': r.id,
                'isStaff': r.is_staff,
                'staffName': r.staff_name if r.is_staff else None,
                'message': r.message,
                'date': r.created_at_jalali,
            }
            for r in ticket.responses.all()
        ]

        return success_response({
            'ticketId': ticket.ticket_id,
            'subject': ticket.subject,
            'status': ticket.status,
            'statusLabel': ticket.status_label,
            'createdAt': ticket.created_at_jalali,
            'responses': responses_data,
        })
