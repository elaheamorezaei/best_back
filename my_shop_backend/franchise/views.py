from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import FranchiseApplication
from .serializers import FranchiseApplySerializer


def _generate_tracking_code():
    year = timezone.now().year
    count = FranchiseApplication.objects.count() + 1
    return f"FRN-{year}-{count:05d}"


class FranchiseApplyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FranchiseApplySerializer(data=request.data)
        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()))
            message = str(first_error[0]) if isinstance(first_error, list) else str(first_error)
            return Response({'success': False, 'message': message}, status=422)

        data = serializer.validated_data
        tracking_code = _generate_tracking_code()

        application = FranchiseApplication.objects.create(
            tracking_code=tracking_code,
            full_name=data['fullName'],
            phone=data['phone'],
            email=data.get('email', ''),
            city=data['city'],
            province=data['province'],
            franchise_type=data['franchiseType'],
            investment_range=data['investmentRange'],
            has_sales_experience=data['hasSalesExperience'],
            description=data.get('description', ''),
        )

        return Response({
            'success': True,
            'message': 'درخواست نمایندگی با موفقیت ثبت شد',
            'data': {
                'trackingCode': application.tracking_code,
                'createdAt': application.created_at.isoformat(),
            },
        }, status=201)
