import datetime
import jdatetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from core.responses import success_response, error_response
from .models import DeliveryTimeSlot

_PERSIAN_WEEKDAYS = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه', 'یکشنبه']
_PERSIAN_MONTHS = [
    'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
]

DELIVERY_COSTS = {
    'normal': 35000,
    'express': 70000,
}


def _jalali_day_label(greg_date):
    jdt = jdatetime.date.fromgregorian(date=greg_date)
    weekday_idx = greg_date.weekday()
    weekday_name = _PERSIAN_WEEKDAYS[weekday_idx]
    month_name = _PERSIAN_MONTHS[jdt.month - 1]
    return f"{weekday_name} {jdt.day} {month_name}", f"{jdt.year}/{jdt.month:02d}/{jdt.day:02d}"


class DeliveryOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        slots = DeliveryTimeSlot.objects.filter(is_active=True)
        slot_data = [
            {'id': s.id, 'label': s.label, 'from': str(s.from_time)[:5], 'to': str(s.to_time)[:5]}
            for s in slots
        ]

        today = datetime.date.today()
        days = []
        offset = 1
        while len(days) < 7:
            candidate = today + datetime.timedelta(days=offset)
            label, value = _jalali_day_label(candidate)
            days.append({'label': label, 'value': value})
            offset += 1

        data = {
            'types': [
                {'id': 'normal', 'label': 'ارسال عادی', 'cost': DELIVERY_COSTS['normal']},
                {'id': 'express', 'label': 'ارسال اکسپرس', 'cost': DELIVERY_COSTS['express']},
            ],
            'days': days,
            'slots': slot_data,
        }
        return success_response(data)


class DeliveryCostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        delivery_type = request.query_params.get('type', 'normal')
        cost = DELIVERY_COSTS.get(delivery_type)
        if cost is None:
            return error_response("نوع ارسال نامعتبر است", status=400)
        return success_response({'type': delivery_type, 'cost': cost})
