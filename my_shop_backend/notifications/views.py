import math
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.responses import success_response, error_response
from core.utils import to_persian_date
from .models import Notification


class NotificationListView(APIView):
    """GET /profile/messages"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(user=request.user)

        msg_type = request.query_params.get('type', '').strip()
        if msg_type in (Notification.TYPE_DISCOUNT, Notification.TYPE_INFO,
                        Notification.TYPE_WARNING, Notification.TYPE_SYSTEM):
            qs = qs.filter(type=msg_type)

        is_read_param = request.query_params.get('isRead', '').strip().lower()
        if is_read_param == 'true':
            qs = qs.filter(is_read=True)
        elif is_read_param == 'false':
            qs = qs.filter(is_read=False)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
        except (ValueError, TypeError):
            page = 1

        limit = 10
        total = qs.count()
        total_pages = math.ceil(total / limit) if total else 1
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        items = list(qs[(page - 1) * limit: page * limit])

        messages = [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'date': to_persian_date(n.created_at),
                'isRead': n.is_read,
                'type': n.type,
            }
            for n in items
        ]

        return success_response({
            'messages': messages,
            'unreadCount': unread_count,
            'pagination': {
                'page': page,
                'total': total,
                'totalPages': total_pages,
            },
        })


class MarkNotificationReadView(APIView):
    """PUT /profile/messages/{messageId}/read"""
    permission_classes = [IsAuthenticated]

    def put(self, request, message_id):
        try:
            notification = Notification.objects.get(pk=message_id, user=request.user)
        except Notification.DoesNotExist:
            return error_response("پیام یافت نشد", status=404)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'success': True, 'message': 'پیام به عنوان خوانده شده علامت‌گذاری شد'})


class MarkAllNotificationsReadView(APIView):
    """PUT /profile/messages/read-all"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'success': True, 'message': 'همه پیام‌ها خوانده شدند'})
