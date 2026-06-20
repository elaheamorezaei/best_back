import jdatetime

_PERSIAN_MONTHS = [
    'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند',
]


def to_persian_date(dt):
    try:
        jdt = jdatetime.datetime.fromgregorian(datetime=dt)
        return f"{jdt.day} {_PERSIAN_MONTHS[jdt.month - 1]} {jdt.year}"
    except Exception:
        return str(dt.date())
