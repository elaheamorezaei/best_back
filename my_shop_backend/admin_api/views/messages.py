from rest_framework.views import APIView
from rest_framework.response import Response

from admin_api.permissions import IsAdminUser
from contact.models import ContactTicket, ContactTicketResponse
from core.utils import to_persian_date


def _serialize_ticket(ticket):
    responses = list(ticket.responses.all())
    last_reply = None
    replied_at = None
    is_replied = False
    for r in responses:
        if r.is_staff:
            is_replied = True
            last_reply = r.message
            replied_at = r.created_at.isoformat()

    return {
        'id': ticket.id,
        'name': ticket.full_name,
        'email': ticket.email,
        'phone': ticket.phone,
        'subject': ticket.subject,
        'message': ticket.message,
        'isRead': ticket.status != ContactTicket.STATUS_OPEN,
        'isReplied': is_replied,
        'reply': last_reply,
        'repliedAt': replied_at,
        'status': ticket.status,
        'createdAt': ticket.created_at.isoformat(),
    }


class AdminMessageListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = ContactTicket.objects.prefetch_related('responses').order_by('-created_at')

        if request.query_params.get('isRead') == 'false':
            qs = qs.filter(status=ContactTicket.STATUS_OPEN)
        elif request.query_params.get('isRead') == 'true':
            qs = qs.exclude(status=ContactTicket.STATUS_OPEN)

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(full_name__icontains=search) | qs.filter(subject__icontains=search)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = max(1, min(100, int(request.query_params.get('pageSize', 20))))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        total = qs.count()
        start = (page - 1) * page_size
        items = list(qs[start:start + page_size])

        return Response({
            'results': [_serialize_ticket(t) for t in items],
            'count': total,
            'next': None,
            'previous': None,
        })


class AdminMessageDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            ticket = ContactTicket.objects.prefetch_related('responses').get(pk=pk)
        except ContactTicket.DoesNotExist:
            return Response({'error': {'message': 'پیام یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        if ticket.status == ContactTicket.STATUS_OPEN:
            ticket.status = ContactTicket.STATUS_IN_PROGRESS
            ticket.save(update_fields=['status'])

        return Response(_serialize_ticket(ticket))

    def delete(self, request, pk):
        try:
            ticket = ContactTicket.objects.get(pk=pk)
        except ContactTicket.DoesNotExist:
            return Response({'error': {'message': 'پیام یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        ticket.delete()
        return Response(status=204)


class AdminMessageReplyView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            ticket = ContactTicket.objects.get(pk=pk)
        except ContactTicket.DoesNotExist:
            return Response({'error': {'message': 'پیام یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        reply_text = request.data.get('reply', '').strip()
        if not reply_text:
            return Response({'error': {'message': 'متن پاسخ الزامی است', 'code': 'MISSING_REPLY'}}, status=400)

        profile = getattr(request.user, 'profile', None)
        staff_name = profile.full_name if profile and profile.full_name else request.user.username

        ContactTicketResponse.objects.create(
            ticket=ticket,
            message=reply_text,
            is_staff=True,
            staff_name=staff_name,
        )

        ticket.status = ContactTicket.STATUS_RESOLVED
        ticket.save(update_fields=['status'])

        ticket.refresh_from_db()
        data = _serialize_ticket(ticket)
        data['isReplied'] = True
        return Response(data)


class AdminMessageMarkReadView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            ticket = ContactTicket.objects.get(pk=pk)
        except ContactTicket.DoesNotExist:
            return Response({'error': {'message': 'پیام یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        if ticket.status == ContactTicket.STATUS_OPEN:
            ticket.status = ContactTicket.STATUS_IN_PROGRESS
            ticket.save(update_fields=['status'])
        return Response({'isRead': True})


class AdminMessageBulkDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': {'message': 'ids الزامی است', 'code': 'MISSING_IDS'}}, status=400)
        deleted, _ = ContactTicket.objects.filter(pk__in=ids).delete()
        return Response({'deleted': deleted})
