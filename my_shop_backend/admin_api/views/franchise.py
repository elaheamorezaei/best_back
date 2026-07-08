from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from admin_api.permissions import IsAdminUser
from franchise.models import FranchiseApplication


def _serialize(app):
    return {
        'id': app.id,
        'trackingCode': app.tracking_code,
        'fullName': app.full_name,
        'phone': app.phone,
        'email': app.email,
        'city': app.city,
        'province': app.province,
        'franchiseType': app.franchise_type,
        'investmentRange': app.investment_range,
        'hasSalesExperience': app.has_sales_experience,
        'description': app.description,
        'status': app.status,
        'adminNote': app.admin_note,
        'reviewedAt': app.reviewed_at.isoformat() if app.reviewed_at else None,
        'createdAt': app.created_at.isoformat(),
    }


class AdminFranchiseListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = FranchiseApplication.objects.all()

        status = request.query_params.get('status')
        if status in (FranchiseApplication.STATUS_PENDING,
                      FranchiseApplication.STATUS_APPROVED,
                      FranchiseApplication.STATUS_REJECTED):
            qs = qs.filter(status=status)

        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                full_name__icontains=search
            ) | qs.filter(
                phone__icontains=search
            ) | qs.filter(
                tracking_code__icontains=search
            )

        province = request.query_params.get('province', '').strip()
        if province:
            qs = qs.filter(province__icontains=province)

        try:
            page = max(1, int(request.query_params.get('page', 1)))
            page_size = max(1, min(100, int(request.query_params.get('pageSize', 20))))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        total = qs.count()
        start = (page - 1) * page_size
        items = list(qs[start:start + page_size])

        return Response({
            'results': [_serialize(a) for a in items],
            'count': total,
            'page': page,
            'pageSize': page_size,
            'totalPages': (total + page_size - 1) // page_size,
        })


class AdminFranchiseDetailView(APIView):
    permission_classes = [IsAdminUser]

    def _get_object(self, pk):
        try:
            return FranchiseApplication.objects.get(pk=pk)
        except FranchiseApplication.DoesNotExist:
            return None

    def get(self, request, pk):
        app = self._get_object(pk)
        if not app:
            return Response({'error': {'message': 'درخواست یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        return Response(_serialize(app))

    def patch(self, request, pk):
        app = self._get_object(pk)
        if not app:
            return Response({'error': {'message': 'درخواست یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        if 'adminNote' in request.data:
            app.admin_note = request.data['adminNote']
            app.save(update_fields=['admin_note'])

        return Response(_serialize(app))

    def delete(self, request, pk):
        app = self._get_object(pk)
        if not app:
            return Response({'error': {'message': 'درخواست یافت نشد', 'code': 'NOT_FOUND'}}, status=404)
        app.delete()
        return Response(status=204)


class AdminFranchiseApproveView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            app = FranchiseApplication.objects.get(pk=pk)
        except FranchiseApplication.DoesNotExist:
            return Response({'error': {'message': 'درخواست یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        app.status = FranchiseApplication.STATUS_APPROVED
        app.admin_note = request.data.get('adminNote', app.admin_note)
        app.reviewed_at = timezone.now()
        app.save(update_fields=['status', 'admin_note', 'reviewed_at'])

        return Response({
            'success': True,
            'message': 'درخواست نمایندگی تایید شد',
            'data': _serialize(app),
        })


class AdminFranchiseRejectView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            app = FranchiseApplication.objects.get(pk=pk)
        except FranchiseApplication.DoesNotExist:
            return Response({'error': {'message': 'درخواست یافت نشد', 'code': 'NOT_FOUND'}}, status=404)

        app.status = FranchiseApplication.STATUS_REJECTED
        app.admin_note = request.data.get('adminNote', app.admin_note)
        app.reviewed_at = timezone.now()
        app.save(update_fields=['status', 'admin_note', 'reviewed_at'])

        return Response({
            'success': True,
            'message': 'درخواست نمایندگی رد شد',
            'data': _serialize(app),
        })
