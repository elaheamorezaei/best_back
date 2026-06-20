from django.db import migrations


def seed_terms(apps, schema_editor):
    TermsMetadata = apps.get_model('terms', 'TermsMetadata')
    Term = apps.get_model('terms', 'Term')
    WalletTermsSection = apps.get_model('terms', 'WalletTermsSection')

    TermsMetadata.objects.get_or_create(
        pk=1,
        defaults={
            'version': '2.1',
            'last_updated': '1403/12/01',
            'hero_title': 'شرایط و قوانین بست',
            'hero_subtitle': 'لطفاً قبل از استفاده از خدمات بست، شرایط و قوانین زیر را به دقت مطالعه فرمایید.',
            'wallet_title': 'شرایط استفاده از کیف پول',
        },
    )

    terms = [
        ('قوانین خرید از بست چیست؟', 'خرید از بست مستلزم پذیرش کامل شرایط و قوانین این پلتفرم است. کاربران باید اطلاعات صحیح وارد کنند و مسئولیت تراکنش‌های انجام‌شده را بر عهده بگیرند.', 1),
        ('شرایط بازگشت کالا چگونه است؟', 'بازگشت کالا تا ۷ روز پس از دریافت، با حفظ بسته‌بندی اصلی و در صورت عدم استفاده امکان‌پذیر است. هزینه ارسال برگشتی بر عهده خریدار است.', 2),
        ('حریم خصوصی کاربران چگونه حفظ می‌شود؟', 'اطلاعات شخصی کاربران نزد ما محرمانه است و هرگز به اشخاص ثالث منتقل نمی‌شود مگر در موارد قانونی.', 3),
        ('نحوه پرداخت و امنیت تراکنش‌ها', 'تمام پرداخت‌ها از طریق درگاه‌های بانکی معتبر و با رمزگذاری SSL انجام می‌شود. اطلاعات کارت شما ذخیره نمی‌شود.', 4),
        ('مسئولیت فروشندگان در قبال محصولات', 'فروشندگان متعهد هستند اطلاعات دقیق و صادقانه‌ای از محصولات ارائه دهند. بست در صورت تخلف، حق تعلیق حساب فروشنده را دارد.', 5),
    ]

    for question, answer, order in terms:
        Term.objects.get_or_create(
            order=order,
            defaults={'question': question, 'answer': answer, 'is_active': True},
        )

    sections = [
        ('فعال‌سازی کیف پول', 'برای استفاده از کیف پول، ابتدا باید آن را از طریق ارسال کد تأیید به شماره موبایل خود فعال کنید.', 1),
        ('شارژ کیف پول', 'حداقل مبلغ شارژ ۱۰۰,۰۰۰ تومان و حداکثر ۲۰۰,۰۰۰,۰۰۰ تومان است. شارژ پس از تأیید درگاه بانکی به‌صورت فوری انجام می‌شود.', 2),
        ('برداشت از کیف پول', 'برداشت حداقل ۵۰,۰۰۰ تومان است. درخواست‌های بالای ۱,۰۰۰,۰۰۰ تومان پس از بررسی تیم مالی در ۲ تا ۳ روز کاری انجام می‌شود.', 3),
        ('انقضا و اعتبار موجودی', 'موجودی کیف پول انقضا ندارد و تا زمانی که حساب کاربری فعال است، نگهداری می‌شود.', 4),
    ]

    for title, content, order in sections:
        WalletTermsSection.objects.get_or_create(
            order=order,
            defaults={'title': title, 'content': content},
        )


def unseed_terms(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('terms', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_terms, unseed_terms),
    ]
