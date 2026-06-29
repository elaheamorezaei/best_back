import io
import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone

User = get_user_model()


def _make_image(color=(100, 150, 200), size=(400, 300), name='img.jpg'):
    try:
        from PIL import Image
        img = Image.new('RGB', size, color=color)
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        return ContentFile(buf.read(), name=name)
    except ImportError:
        return None


COLORS = [
    (220, 80, 80), (80, 150, 220), (80, 200, 120),
    (220, 180, 60), (160, 80, 200), (80, 200, 200),
    (200, 120, 60), (120, 120, 180),
]


class Command(BaseCommand):
    help = 'Seed database with comprehensive test data for frontend testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Clear existing seeded data before inserting'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self._clear_data()

        self.stdout.write('🌱 شروع seed...')
        self._create_admin()
        self._create_users()
        self._create_locations()
        self._create_delivery_slots()
        self._create_categories()
        self._create_products()
        self._create_blog()
        self._create_banners()
        self._create_sliders()
        self._create_faq()
        self._create_discounts()
        self.stdout.write(self.style.SUCCESS('✅ Seed با موفقیت انجام شد!'))

    # ─── Clear ────────────────────────────────────────────────────────────────

    def _clear_data(self):
        from products.models import (Category, Product, ProductColor,
                                      ProductWarranty, ProductFeature,
                                      ProductSpec, ProductIntro,
                                      ProductEditorialReview)
        from blog.models import BlogCategory, BlogPost
        from banners.models import Banner
        from slider.models import Slider
        from faq.models import FAQCategory, FAQ
        from discounts.models import DiscountCode, GiftCard
        from locations.models import Province, City
        from delivery.models import DeliveryTimeSlot

        self.stdout.write('🗑  پاک‌سازی داده‌های قبلی...')
        ProductEditorialReview.objects.all().delete()
        ProductIntro.objects.all().delete()
        ProductSpec.objects.all().delete()
        ProductFeature.objects.all().delete()
        ProductWarranty.objects.all().delete()
        ProductColor.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        BlogPost.objects.all().delete()
        BlogCategory.objects.all().delete()
        Banner.objects.all().delete()
        Slider.objects.all().delete()
        FAQ.objects.all().delete()
        FAQCategory.objects.all().delete()
        DiscountCode.objects.all().delete()
        GiftCard.objects.all().delete()
        City.objects.all().delete()
        Province.objects.all().delete()
        DeliveryTimeSlot.objects.all().delete()

    # ─── Admin & Users ────────────────────────────────────────────────────────

    def _create_admin(self):
        from users.models import UserProfile
        email = 'admin@shop.com'
        if not User.objects.filter(email=email).exists():
            admin = User.objects.create_superuser(
                username='admin',
                email=email,
                password='Admin@1234',
            )
            admin.first_name = 'مدیر'
            admin.last_name = 'سیستم'
            admin.save()
            UserProfile.objects.get_or_create(
                user=admin,
                defaults={
                    'phone_number': '09100000000',
                    'full_name': 'مدیر سیستم',
                    'role': 'superadmin',
                }
            )
            self.stdout.write(f'  ✔ ادمین ساخته شد: {email} / Admin@1234')
        else:
            self.stdout.write(f'  — ادمین از قبل موجود: {email}')

    def _create_users(self):
        from users.models import UserProfile
        users_data = [
            {'username': 'user1', 'email': 'user1@test.com', 'password': 'Test@1234',
             'first_name': 'علی', 'last_name': 'احمدی',
             'phone': '09111111111', 'full_name': 'علی احمدی', 'gender': 'آقا'},
            {'username': 'user2', 'email': 'user2@test.com', 'password': 'Test@1234',
             'first_name': 'مریم', 'last_name': 'رضایی',
             'phone': '09222222222', 'full_name': 'مریم رضایی', 'gender': 'خانم'},
            {'username': 'user3', 'email': 'user3@test.com', 'password': 'Test@1234',
             'first_name': 'رضا', 'last_name': 'محمدی',
             'phone': '09333333333', 'full_name': 'رضا محمدی', 'gender': 'آقا'},
        ]
        for d in users_data:
            if not User.objects.filter(email=d['email']).exists():
                u = User.objects.create_user(
                    username=d['username'], email=d['email'],
                    password=d['password'],
                    first_name=d['first_name'], last_name=d['last_name'],
                )
                UserProfile.objects.get_or_create(
                    user=u,
                    defaults={
                        'phone_number': d['phone'],
                        'full_name': d['full_name'],
                        'gender': d['gender'],
                    }
                )
        self.stdout.write('  ✔ کاربران ساخته شدند')

    # ─── Locations ────────────────────────────────────────────────────────────

    def _create_locations(self):
        from locations.models import Province, City
        provinces = {
            'تهران': ['تهران', 'کرج', 'ورامین'],
            'اصفهان': ['اصفهان', 'کاشان', 'نجف‌آباد'],
            'خراسان رضوی': ['مشهد', 'نیشابور', 'سبزوار'],
            'فارس': ['شیراز', 'مرودشت', 'جهرم'],
            'آذربایجان شرقی': ['تبریز', 'مراغه', 'اهر'],
        }
        for pname, cities in provinces.items():
            p, _ = Province.objects.get_or_create(name=pname)
            for cname in cities:
                City.objects.get_or_create(province=p, name=cname)
        self.stdout.write('  ✔ استان‌ها و شهرها ساخته شدند')

    # ─── Delivery Slots ───────────────────────────────────────────────────────

    def _create_delivery_slots(self):
        from delivery.models import DeliveryTimeSlot
        import datetime
        slots = [
            ('صبح (۸-۱۲)', datetime.time(8, 0), datetime.time(12, 0)),
            ('ظهر (۱۲-۱۶)', datetime.time(12, 0), datetime.time(16, 0)),
            ('عصر (۱۶-۲۰)', datetime.time(16, 0), datetime.time(20, 0)),
        ]
        for label, from_t, to_t in slots:
            DeliveryTimeSlot.objects.get_or_create(
                label=label,
                defaults={'from_time': from_t, 'to_time': to_t, 'is_active': True}
            )
        self.stdout.write('  ✔ زمان‌بندی ارسال ساخته شد')

    # ─── Categories ──────────────────────────────────────────────────────────

    def _create_categories(self):
        from products.models import Category
        main_cats = [
            {'name': 'موبایل و تبلت', 'slug': 'mobile-tablet', 'icon': 'smartphone', 'order': 1,
             'desc': 'انواع گوشی‌های هوشمند، تبلت و لوازم جانبی',
             'children': [
                 {'name': 'گوشی موبایل', 'slug': 'mobile-phones', 'order': 1},
                 {'name': 'تبلت', 'slug': 'tablets', 'order': 2},
             ]},
            {'name': 'لپ‌تاپ و کامپیوتر', 'slug': 'laptop-computer', 'icon': 'laptop', 'order': 2,
             'desc': 'لپ‌تاپ، کامپیوتر و لوازم جانبی',
             'children': [
                 {'name': 'لپ‌تاپ', 'slug': 'laptops', 'order': 1},
                 {'name': 'کامپیوتر رومیزی', 'slug': 'desktop-computers', 'order': 2},
             ]},
            {'name': 'صوتی و تصویری', 'slug': 'audio-video', 'icon': 'headphones', 'order': 3,
             'desc': 'تلویزیون، هدفون، بلندگو و تجهیزات صوتی-تصویری',
             'children': [
                 {'name': 'هدفون و هندزفری', 'slug': 'headphones-earphones', 'order': 1},
                 {'name': 'بلندگو', 'slug': 'speakers', 'order': 2},
             ]},
            {'name': 'خانه هوشمند', 'slug': 'smart-home', 'icon': 'home', 'order': 4,
             'desc': 'دستگاه‌های هوشمند خانگی',
             'children': [
                 {'name': 'دستیار صوتی', 'slug': 'smart-speakers', 'order': 1},
                 {'name': 'دوربین هوشمند', 'slug': 'smart-cameras', 'order': 2},
             ]},
        ]
        self.categories = {}
        for mc in main_cats:
            color = random.choice(COLORS)
            img = _make_image(color, (300, 300), f"cat_{mc['slug']}.jpg")
            cat, _ = Category.objects.get_or_create(
                slug=mc['slug'],
                defaults={
                    'name': mc['name'],
                    'description': mc['desc'],
                    'icon': mc['icon'],
                    'is_main': True,
                    'is_active': True,
                    'order': mc['order'],
                }
            )
            if img and not cat.image:
                cat.image.save(f"cat_{mc['slug']}.jpg", img, save=True)
            self.categories[mc['slug']] = cat

            for child in mc['children']:
                c_img = _make_image(random.choice(COLORS), (300, 300), f"cat_{child['slug']}.jpg")
                child_cat, _ = Category.objects.get_or_create(
                    slug=child['slug'],
                    defaults={
                        'name': child['name'],
                        'parent': cat,
                        'is_active': True,
                        'order': child['order'],
                    }
                )
                if c_img and not child_cat.image:
                    child_cat.image.save(f"cat_{child['slug']}.jpg", c_img, save=True)
                self.categories[child['slug']] = child_cat

        self.stdout.write('  ✔ دسته‌بندی‌ها ساخته شدند')

    # ─── Products ─────────────────────────────────────────────────────────────

    def _create_products(self):
        from products.models import (Product, ProductColor, ProductWarranty,
                                      ProductFeature, ProductSpec,
                                      ProductIntro, ProductEditorialReview)
        products_data = [
            # ── موبایل ─────────────────────────────────────────────────────
            {
                'name': 'سامسونگ Galaxy S24 Ultra', 'slug': 'samsung-galaxy-s24-ultra',
                'sku': 'SAM-S24U-001', 'brand': 'سامسونگ', 'model': 'SM-S928B',
                'category': 'mobile-phones', 'price': 45000000, 'compare_price': 48000000,
                'stock': 25, 'min_stock': 5, 'is_featured': True, 'is_new': True,
                'tags': ['گوشی', 'سامسونگ', 'فلگشیپ', 'اندروید'],
                'short_desc': 'قدرتمندترین گوشی سامسونگ با دوربین ۲۰۰ مگاپیکسل',
                'desc': 'سامسونگ Galaxy S24 Ultra با پردازنده Snapdragon 8 Gen 3 و دوربین ۲۰۰ مگاپیکسلی، تجربه‌ای بی‌نظیر ارائه می‌دهد.',
                'colors': [('مشکی تیتانیوم', '#1A1A1A'), ('بژ تیتانیوم', '#C8B8A2'), ('بنفش تیتانیوم', '#7B68EE')],
                'warranties': ['گارانتی ۱۸ ماهه سامسونگ', 'ضمانت اصالت کالا'],
                'features': [('پردازنده', 'Snapdragon 8 Gen 3'), ('رم', '12 GB'), ('حافظه', '256 GB'), ('دوربین', '200 MP')],
                'specs': [('وزن', '232 گرم'), ('ابعاد', '79×162×8.6 میلیمتر'), ('باتری', '5000 mAh'), ('شارژ سریع', '45W'), ('سیستم‌عامل', 'Android 14')],
                'intro': 'سامسونگ با این گوشی مرزهای فناوری موبایل را به چالش کشیده است. دوربین ۲۰۰ مگاپیکسلی با قابلیت زوم ۱۰۰ برابری، عکاسی حرفه‌ای را در اختیار شما می‌گذارد.',
                'pros': ['دوربین فوق‌العاده', 'طراحی پریمیوم', 'باتری قوی'], 'cons': ['قیمت بالا', 'حجم و وزن زیاد'],
            },
            {
                'name': 'اپل iPhone 15 Pro Max', 'slug': 'apple-iphone-15-pro-max',
                'sku': 'APL-IP15PM-001', 'brand': 'اپل', 'model': 'A3105',
                'category': 'mobile-phones', 'price': 62000000, 'compare_price': 65000000,
                'stock': 15, 'min_stock': 3, 'is_featured': True, 'is_sale': True,
                'tags': ['آیفون', 'اپل', 'iOS', 'فلگشیپ'],
                'short_desc': 'آیفون ۱۵ پرو مکس با چیپ A17 Pro و بدنه تیتانیوم',
                'desc': 'آیفون ۱۵ پرو مکس با چیپ A17 Pro، بدنه تیتانیوم و سیستم دوربین پیشرفته، بهترین آیفون ساخته شده تاکنون است.',
                'colors': [('تیتانیوم طبیعی', '#C4B49A'), ('تیتانیوم مشکی', '#3D3D3D'), ('تیتانیوم سفید', '#F0EDE8')],
                'warranties': ['گارانتی ۱۸ ماهه شرکتی', 'پشتیبانی اپل'],
                'features': [('چیپ', 'A17 Pro'), ('رم', '8 GB'), ('حافظه', '256 GB'), ('دوربین اصلی', '48 MP')],
                'specs': [('وزن', '221 گرم'), ('ابعاد', '77×159.9×8.25 میلیمتر'), ('باتری', '4422 mAh'), ('شارژ', '27W'), ('سیستم‌عامل', 'iOS 17')],
                'intro': 'اپل با آیفون ۱۵ پرو مکس استانداردهای جدیدی در صنعت موبایل تعریف کرده است. بدنه تیتانیوم سبک و محکم، همراه با چیپ A17 Pro، قدرتمندترین آیفون تاریخ را ساخته است.',
                'pros': ['عملکرد بی‌نظیر', 'بدنه تیتانیوم', 'اکوسیستم اپل'], 'cons': ['قیمت بسیار بالا', 'شارژر جداگانه'],
            },
            {
                'name': 'شیائومی Redmi Note 13 Pro', 'slug': 'xiaomi-redmi-note-13-pro',
                'sku': 'XMI-RN13P-001', 'brand': 'شیائومی', 'model': '2312DRA50G',
                'category': 'mobile-phones', 'price': 12500000, 'compare_price': 14000000,
                'stock': 50, 'min_stock': 10, 'is_new': True, 'is_sale': True,
                'tags': ['شیائومی', 'ردمی', 'میان‌رده', 'اقتصادی'],
                'short_desc': 'بهترین گوشی میان‌رده با دوربین ۲۰۰ مگاپیکسل',
                'desc': 'ردمی نوت ۱۳ پرو با دوربین ۲۰۰ مگاپیکسلی و صفحه‌نمایش AMOLED 120Hz، بهترین ارزش را در رده میان‌رده ارائه می‌دهد.',
                'colors': [('مشکی اوشن', '#1C2333'), ('سبز جنگلی', '#2D5016'), ('بنفش لاوندر', '#967BB6')],
                'warranties': ['گارانتی ۱۲ ماهه'],
                'features': [('پردازنده', 'Snapdragon 7s Gen 2'), ('رم', '8 GB'), ('حافظه', '256 GB'), ('دوربین', '200 MP')],
                'specs': [('وزن', '187 گرم'), ('ابعاد', '74.2×161.1×8 میلیمتر'), ('باتری', '5000 mAh'), ('شارژ سریع', '67W'), ('نمایشگر', 'AMOLED 6.67 اینچ')],
                'intro': 'ردمی نوت ۱۳ پرو ثابت می‌کند که نیازی به پرداخت چند ده میلیون تومان برای داشتن یک گوشی خوب نیست.',
                'pros': ['قیمت مناسب', 'دوربین عالی', 'شارژ سریع'], 'cons': ['پردازنده میان‌رده', 'بدون NFC'],
            },
            # ── تبلت ──────────────────────────────────────────────────────
            {
                'name': 'اپل iPad Pro 12.9 M2', 'slug': 'apple-ipad-pro-12-9-m2',
                'sku': 'APL-IPDP129-001', 'brand': 'اپل', 'model': 'MNXR3',
                'category': 'tablets', 'price': 38000000, 'compare_price': 40000000,
                'stock': 10, 'min_stock': 2, 'is_featured': True,
                'tags': ['آیپد', 'اپل', 'تبلت', 'پرو'],
                'short_desc': 'آیپد پرو با چیپ M2 و صفحه نمایش Liquid Retina XDR',
                'desc': 'آیپد پرو ۱۲.۹ اینچ با چیپ M2 قدرتمندترین تبلت بازار است که می‌تواند جایگزین لپ‌تاپ شود.',
                'colors': [('نقره‌ای', '#C0C0C0'), ('خاکستری فضایی', '#4A4A4A')],
                'warranties': ['گارانتی ۱۸ ماهه اپل'],
                'features': [('چیپ', 'Apple M2'), ('رم', '8 GB'), ('حافظه', '128 GB'), ('نمایشگر', '12.9 اینچ Liquid Retina XDR')],
                'specs': [('وزن', '682 گرم'), ('ابعاد', '280.6×214.9×6.4 میلیمتر'), ('باتری', '10541 mAh'), ('اتصال', 'Wi-Fi 6E, 5G'), ('سیستم‌عامل', 'iPadOS 17')],
                'intro': 'آیپد پرو با چیپ M2 اپل قدرتی باورنکردنی در قالب یک تبلت نازک و سبک ارائه می‌دهد.',
                'pros': ['بهترین نمایشگر تبلت', 'چیپ فوق‌قوی', 'اکوسیستم اپل'], 'cons': ['قیمت بالا', 'بدون USB-A'],
            },
            # ── لپ‌تاپ ────────────────────────────────────────────────────
            {
                'name': 'ایسوس ZenBook 14 OLED', 'slug': 'asus-zenbook-14-oled',
                'sku': 'ASUS-ZB14-001', 'brand': 'ایسوس', 'model': 'UX3402VA',
                'category': 'laptops', 'price': 32000000, 'compare_price': 35000000,
                'stock': 8, 'min_stock': 2, 'is_featured': True, 'is_new': True,
                'tags': ['لپ‌تاپ', 'ایسوس', 'OLED', 'اولترابوک'],
                'short_desc': 'لپ‌تاپ سبک با صفحه نمایش OLED 2.8K',
                'desc': 'زن‌بوک ۱۴ با صفحه نمایش OLED خیره‌کننده و پردازنده Core i7 نسل ۱۳، ترکیب بی‌نظیری از قدرت و زیبایی است.',
                'colors': [('آبی پاینامل', '#1E5F8E'), ('بژ برونزه', '#C4A882')],
                'warranties': ['گارانتی ۱۸ ماهه گلوبال ایسوس', 'پشتیبانی فنی ۲ ساله'],
                'features': [('پردازنده', 'Intel Core i7-1360P'), ('رم', '16 GB LPDDR5'), ('حافظه', '512 GB NVMe SSD'), ('نمایشگر', 'OLED 2.8K 90Hz')],
                'specs': [('وزن', '1.39 کیلوگرم'), ('باتری', '75Wh'), ('شارژ', '65W USB-C'), ('سیستم‌عامل', 'Windows 11'), ('اتصال', 'Wi-Fi 6E, Bluetooth 5.3')],
                'intro': 'ایسوس با زن‌بوک ۱۴ OLED نشان داده که می‌توان یک لپ‌تاپ سبک و قابل حمل ساخت که هیچ چیزی را فدا نکند.',
                'pros': ['صفحه OLED زیبا', 'وزن کم', 'طراحی شیک'], 'cons': ['گرم می‌شود زیر بار', 'پورت‌های محدود'],
            },
            {
                'name': 'لنوو ThinkPad X1 Carbon Gen 11', 'slug': 'lenovo-thinkpad-x1-carbon-gen11',
                'sku': 'LNV-X1CG11-001', 'brand': 'لنوو', 'model': '21HM0054',
                'category': 'laptops', 'price': 42000000, 'compare_price': 45000000,
                'stock': 5, 'min_stock': 1, 'is_featured': False,
                'tags': ['لپ‌تاپ', 'لنوو', 'تینک‌پد', 'کسب‌وکار'],
                'short_desc': 'لپ‌تاپ تجاری سبک و بادوام برای حرفه‌ای‌ها',
                'desc': 'تینک‌پد X1 کربن با بدنه کربن فایبر فوق‌سبک و صفحه کلید معروف ThinkPad، انتخاب حرفه‌ای‌های تجاری است.',
                'colors': [('مشکی', '#1A1A1A')],
                'warranties': ['گارانتی ۳ ساله لنوو', 'پشتیبانی تلفنی ۲۴/۷'],
                'features': [('پردازنده', 'Intel Core i7-1365U'), ('رم', '16 GB LPDDR5'), ('حافظه', '512 GB SSD'), ('نمایشگر', 'IPS 14 اینچ 2.8K')],
                'specs': [('وزن', '1.12 کیلوگرم'), ('باتری', '57Wh'), ('شارژ', 'Rapid Charge 65W'), ('سیستم‌عامل', 'Windows 11 Pro'), ('اتصال', 'Wi-Fi 6E, 4G LTE اختیاری')],
                'intro': 'تینک‌پد X1 کربن یکی از محبوب‌ترین لپ‌تاپ‌های تجاری جهان است که استانداردهای نظامی MIL-SPEC را رد می‌کند.',
                'pros': ['فوق‌العاده سبک', 'دوام بالا', 'صفحه کلید بهترین'], 'cons': ['قیمت بالا', 'GPU ضعیف'],
            },
            # ── هدفون ─────────────────────────────────────────────────────
            {
                'name': 'سونی WH-1000XM5', 'slug': 'sony-wh-1000xm5',
                'sku': 'SONY-WH1KM5-001', 'brand': 'سونی', 'model': 'WH-1000XM5',
                'category': 'headphones-earphones', 'price': 8500000, 'compare_price': 9500000,
                'stock': 30, 'min_stock': 5, 'is_featured': True, 'is_best_seller': True,
                'tags': ['هدفون', 'سونی', 'نویزکنسلینگ', 'بلوتوث'],
                'short_desc': 'بهترین هدفون نویز کنسلینگ دنیا',
                'desc': 'سونی WH-1000XM5 با سیستم نویز کنسلینگ پیشرفته و کیفیت صدای استثنایی، تجربه‌ای بی‌نظیر از موسیقی می‌دهد.',
                'colors': [('مشکی', '#1A1A1A'), ('نقره‌ای', '#C0C0C0')],
                'warranties': ['گارانتی ۱۸ ماهه سونی'],
                'features': [('نویز کنسلینگ', 'ANC پیشرفته'), ('باتری', '۳۰ ساعت'), ('اتصال', 'Bluetooth 5.2'), ('کدک', 'LDAC, AAC, SBC')],
                'specs': [('وزن', '250 گرم'), ('درایور', '30 میلیمتر'), ('پاسخ فرکانسی', '4Hz - 40kHz'), ('مقاومت', '16Ω'), ('شارژ', 'USB-C 3 ساعت')],
                'intro': 'WH-1000XM5 نتیجه سال‌ها تحقیق سونی در حوزه صدا و نویز کنسلینگ است. با ۸ میکروفون و پردازنده اختصاصی QN1، هوشمندانه محیط را آنالیز می‌کند.',
                'pros': ['بهترین ANC بازار', 'صدای پریمیوم', 'راحتی بالا'], 'cons': ['قیمت بالا', 'تا شدنی نیست'],
            },
            {
                'name': 'اپل AirPods Pro 2', 'slug': 'apple-airpods-pro-2',
                'sku': 'APL-APP2-001', 'brand': 'اپل', 'model': 'MTJV3',
                'category': 'headphones-earphones', 'price': 7800000, 'compare_price': 8500000,
                'stock': 20, 'min_stock': 4, 'is_featured': True, 'is_sale': True,
                'tags': ['ایرپاد', 'اپل', 'هندزفری', 'TWS'],
                'short_desc': 'هندزفری بی‌سیم اپل با ANC بهبود یافته',
                'desc': 'ایرپاد پرو نسل دوم با ANC ۲ برابر قوی‌تر، صدای فضایی تطبیقی و ظرفیت باتری بهبود یافته.',
                'colors': [('سفید', '#F5F5F5')],
                'warranties': ['گارانتی ۱۸ ماهه اپل'],
                'features': [('چیپ', 'Apple H2'), ('ANC', 'تا ۲۹dB کاهش نویز'), ('باتری', '۶ ساعت + ۳۰ ساعت با کیس'), ('شارژ', 'MagSafe, Lightning, USB-C')],
                'specs': [('وزن هر هندزفری', '5.3 گرم'), ('وزن کیس', '50.8 گرم'), ('اتصال', 'Bluetooth 5.3'), ('مقاومت', 'IPX4')],
                'intro': 'ایرپاد پرو ۲ با صدای فضایی شخصی‌سازی شده و ANC پیشرفته، تجربه‌ای متفاوت از موسیقی ارائه می‌دهد.',
                'pros': ['ANC قوی', 'صدای فضایی', 'یکپارچگی با اپل'], 'cons': ['فقط برای کاربران اپل', 'قیمت بالا'],
            },
            # ── بلندگو ─────────────────────────────────────────────────────
            {
                'name': 'بوز SoundLink Max', 'slug': 'bose-soundlink-max',
                'sku': 'BOSE-SLM-001', 'brand': 'بوز', 'model': 'SoundLink Max',
                'category': 'speakers', 'price': 9200000, 'compare_price': 10000000,
                'stock': 15, 'min_stock': 3, 'is_new': True,
                'tags': ['بلندگو', 'بوز', 'بی‌سیم', 'پرتابل'],
                'short_desc': 'بزرگ‌ترین و قوی‌ترین بلندگوی پرتابل بوز',
                'desc': 'بوز SoundLink Max با صدای قدرتمند و پر حجم، طراحی ضداب و باتری ۲۰ ساعته، همراه ایده‌آل برای فضای باز است.',
                'colors': [('مشکی', '#1A1A1A'), ('آبی سنگی', '#4A6FA5')],
                'warranties': ['گارانتی ۱۲ ماهه بوز'],
                'features': [('توان', '36 وات'), ('باتری', '۲۰ ساعت'), ('اتصال', 'Bluetooth 5.3'), ('مقاومت', 'IP67')],
                'specs': [('وزن', '1.3 کیلوگرم'), ('ابعاد', '243×97×97 میلیمتر'), ('شارژ', 'USB-C'), ('رنج فرکانسی', '55Hz - 20kHz')],
                'intro': 'بلندگوی SoundLink Max از تکنولوژی صوتی پیشرفته بوز استفاده می‌کند تا صدایی قوی و پر از جزئیات ارائه دهد.',
                'pros': ['صدای قوی', 'مقاومت IP67', 'باتری طولانی'], 'cons': ['سنگین', 'قیمت بالا'],
            },
            # ── خانه هوشمند ────────────────────────────────────────────────
            {
                'name': 'اکو دات نسل ۵', 'slug': 'amazon-echo-dot-gen5',
                'sku': 'AMZ-ED5-001', 'brand': 'آمازون', 'model': 'Echo Dot Gen 5',
                'category': 'smart-speakers', 'price': 2800000, 'compare_price': 3200000,
                'stock': 40, 'min_stock': 8, 'is_sale': True, 'is_popular': True,
                'tags': ['اسمارت‌هوم', 'آمازون', 'الکسا', 'بلندگوی هوشمند'],
                'short_desc': 'دستیار صوتی هوشمند با الکسا',
                'desc': 'اکو دات نسل پنجم با دستیار الکسا، می‌تواند خانه شما را هوشمند کند. موسیقی پخش کند، اخبار بدهد و دستگاه‌های هوشمند را کنترل کند.',
                'colors': [('آبی', '#2E86AB'), ('مشکی', '#1A1A1A'), ('سفید', '#F5F5F5')],
                'warranties': ['گارانتی ۱۲ ماهه'],
                'features': [('دستیار', 'Amazon Alexa'), ('بلندگو', '1.73 اینچ'), ('اتصال', 'Wi-Fi 6, Bluetooth 5.0'), ('قابلیت', 'Smart Home Hub')],
                'specs': [('وزن', '304 گرم'), ('ابعاد', '99×99×89 میلیمتر'), ('آداپتور', '15W'), ('میکروفون', '4 عدد')],
                'intro': 'اکو دات ساده‌ترین راه برای ورود به دنیای خانه هوشمند است.',
                'pros': ['قیمت مناسب', 'سهولت استفاده', 'یکپارچگی گسترده'], 'cons': ['به اینترنت نیاز دارد', 'حریم خصوصی'],
            },
            {
                'name': 'دوربین امنیتی هوشمند Wyze Cam v4', 'slug': 'wyze-cam-v4',
                'sku': 'WYZE-CAM4-001', 'brand': 'وایز', 'model': 'Wyze Cam v4',
                'category': 'smart-cameras', 'price': 1500000, 'compare_price': 1800000,
                'stock': 35, 'min_stock': 7, 'is_new': True, 'is_popular': True,
                'tags': ['دوربین', 'هوشمند', 'امنیتی', 'وایز'],
                'short_desc': 'دوربین ۲K با دید در شب رنگی',
                'desc': 'وایز کم v4 با وضوح ۲K، دید در شب رنگی و هوش مصنوعی تشخیص حرکت، امنیت خانه را با هزینه‌ای کم فراهم می‌کند.',
                'colors': [('سفید', '#F5F5F5')],
                'warranties': ['گارانتی ۱۲ ماهه'],
                'features': [('وضوح', '2K 2560×1440'), ('دید شب', 'رنگی تا 9 متر'), ('تشخیص', 'هوش مصنوعی'), ('ذخیره', 'microSD تا 256GB')],
                'specs': [('وزن', '113 گرم'), ('اتصال', 'Wi-Fi 2.4GHz و 5GHz'), ('زاویه دید', '130 درجه'), ('ضدآب', 'IP65')],
                'intro': 'وایز کم v4 ثابت می‌کند که دوربین امنیتی با کیفیت لازم نیست گران باشد.',
                'pros': ['قیمت بسیار مناسب', 'کیفیت 2K', 'نصب آسان'], 'cons': ['نیاز به اشتراک برای برخی امکانات', 'فضای ابری محدود رایگان'],
            },
            {
                'name': 'سامسونگ Galaxy Tab S9 FE', 'slug': 'samsung-galaxy-tab-s9-fe',
                'sku': 'SAM-TABS9FE-001', 'brand': 'سامسونگ', 'model': 'SM-X510',
                'category': 'tablets', 'price': 16500000, 'compare_price': 18000000,
                'stock': 12, 'min_stock': 3, 'is_sale': True,
                'tags': ['تبلت', 'سامسونگ', 'گلکسی', 'اندروید'],
                'short_desc': 'تبلت میان‌رده سامسونگ با قلم S Pen',
                'desc': 'گلکسی Tab S9 FE با نمایشگر بزرگ TFT 10.9 اینچ، قلم S Pen و باتری ۸۰۰۰ میلی‌آمپری، تبلتی عالی برای کار و سرگرمی است.',
                'colors': [('خاکستری', '#808080'), ('بنفش لاوندر', '#967BB6'), ('سبز مینت', '#2E8B57')],
                'warranties': ['گارانتی ۱۸ ماهه سامسونگ'],
                'features': [('پردازنده', 'Exynos 1380'), ('رم', '6 GB'), ('حافظه', '128 GB'), ('S Pen', 'شامل می‌شود')],
                'specs': [('وزن', '523 گرم'), ('نمایشگر', 'TFT 10.9 اینچ'), ('باتری', '8000 mAh'), ('شارژ', '45W'), ('سیستم‌عامل', 'Android 13')],
                'intro': 'گلکسی Tab S9 FE بهترین انتخاب برای کسانی است که به دنبال تجربه ممتاز سامسونگ با بودجه معقول هستند.',
                'pros': ['S Pen رایگان', 'نمایشگر بزرگ', 'باتری قوی'], 'cons': ['نمایشگر TFT نه AMOLED', 'پردازنده میان‌رده'],
            },
        ]

        self.product_objs = []
        for i, pd in enumerate(products_data):
            cat = self.categories.get(pd['category'])
            if not cat:
                continue

            p, created = Product.objects.get_or_create(
                slug=pd['slug'],
                defaults={
                    'name': pd['name'],
                    'sku': pd['sku'],
                    'brand': pd['brand'],
                    'model': pd['model'],
                    'category': cat,
                    'price': pd['price'],
                    'compare_price': pd.get('compare_price'),
                    'stock': pd['stock'],
                    'min_stock': pd['min_stock'],
                    'description': pd['desc'],
                    'short_description': pd['short_desc'],
                    'tags': pd['tags'],
                    'is_active': True,
                    'is_featured': pd.get('is_featured', False),
                    'is_new': pd.get('is_new', False),
                    'is_sale': pd.get('is_sale', False),
                    'is_best_seller': pd.get('is_best_seller', False),
                    'is_popular': pd.get('is_popular', False),
                    'star': round(random.uniform(3.5, 5.0), 1),
                    'sales_count': random.randint(10, 500),
                    'off': random.choice([0, 0, 5, 10, 15, 20]),
                }
            )

            if created:
                color = COLORS[i % len(COLORS)]
                img = _make_image(color, (500, 500), f"product_{p.slug}.jpg")
                if img:
                    p.image.save(f"product_{p.slug}.jpg", img, save=True)

                for cname, chex in pd.get('colors', []):
                    ProductColor.objects.create(product=p, name=cname, hex=chex)

                for j, wtxt in enumerate(pd.get('warranties', [])):
                    ProductWarranty.objects.create(product=p, text=wtxt, order=j)

                for j, (fname, fval) in enumerate(pd.get('features', [])):
                    ProductFeature.objects.create(product=p, name=fname, value=fval, order=j)

                for j, (sname, sval) in enumerate(pd.get('specs', [])):
                    ProductSpec.objects.create(product=p, name=sname, value=sval, order=j)

                if pd.get('intro'):
                    ProductIntro.objects.create(product=p, text=pd['intro'], order=0)

                if pd.get('pros') or pd.get('cons'):
                    ProductEditorialReview.objects.create(
                        product=p,
                        text=f"بررسی تحریریه: {pd['name']}",
                        pros=pd.get('pros', []),
                        cons=pd.get('cons', []),
                    )

            self.product_objs.append(p)

        self.stdout.write(f'  ✔ {len(products_data)} محصول ساخته شد')

    # ─── Blog ─────────────────────────────────────────────────────────────────

    def _create_blog(self):
        from blog.models import BlogCategory, BlogPost

        blog_cats = [
            {'name': 'تکنولوژی', 'slug': 'technology', 'icon': 'cpu', 'order': 1},
            {'name': 'راهنمای خرید', 'slug': 'buying-guide', 'icon': 'shopping-bag', 'order': 2},
            {'name': 'اخبار', 'slug': 'news', 'icon': 'newspaper', 'order': 3},
            {'name': 'آموزش', 'slug': 'tutorial', 'icon': 'book', 'order': 4},
        ]
        self.blog_cats = {}
        for bc in blog_cats:
            obj, _ = BlogCategory.objects.get_or_create(
                slug=bc['slug'],
                defaults={'name': bc['name'], 'icon': bc['icon'], 'order': bc['order']}
            )
            self.blog_cats[bc['slug']] = obj

        posts = [
            {
                'title': 'بهترین گوشی‌های ۲۰۲۴ برای خرید',
                'slug': 'best-phones-2024',
                'category': 'buying-guide',
                'excerpt': 'راهنمای جامع خرید گوشی در سال ۲۰۲۴',
                'content': 'در این مقاله به بررسی بهترین گوشی‌های ۲۰۲۴ می‌پردازیم...',
                'tags': ['گوشی', 'خرید', '۲۰۲۴'], 'is_published': True, 'is_featured': True,
            },
            {
                'title': 'مقایسه iPhone 15 Pro Max با Galaxy S24 Ultra',
                'slug': 'iphone-15-vs-galaxy-s24',
                'category': 'technology',
                'excerpt': 'کدام فلگشیپ ارزش خریدن دارد؟',
                'content': 'آیفون یا سامسونگ؟ این سوالی است که ذهن بسیاری از خریداران را درگیر می‌کند...',
                'tags': ['آیفون', 'سامسونگ', 'مقایسه'], 'is_published': True, 'is_featured': False,
            },
            {
                'title': 'معرفی جدیدترین لپ‌تاپ‌های ۲۰۲۴',
                'slug': 'new-laptops-2024',
                'category': 'news',
                'excerpt': 'آشنایی با لپ‌تاپ‌هایی که امسال معرفی شدند',
                'content': 'سال ۲۰۲۴ سالی پر از معرفی لپ‌تاپ‌های جذاب بود...',
                'tags': ['لپ‌تاپ', 'اخبار', '۲۰۲۴'], 'is_published': True, 'is_featured': True,
            },
            {
                'title': 'چگونه بهترین هدفون را انتخاب کنیم؟',
                'slug': 'how-to-choose-headphones',
                'category': 'tutorial',
                'excerpt': 'راهنمای انتخاب هدفون مناسب برای نیازهای شما',
                'content': 'انتخاب هدفون مناسب می‌تواند گیج‌کننده باشد. در این راهنما...',
                'tags': ['هدفون', 'آموزش', 'راهنما'], 'is_published': True, 'is_featured': False,
            },
            {
                'title': 'تکنولوژی OLED چیست و چرا مهم است؟',
                'slug': 'what-is-oled',
                'category': 'technology',
                'excerpt': 'آشنایی با فناوری OLED و مزایای آن',
                'content': 'OLED مخفف Organic Light-Emitting Diode است...',
                'tags': ['OLED', 'نمایشگر', 'فناوری'], 'is_published': True, 'is_featured': False,
            },
            {
                'title': 'راهنمای خرید تبلت در ۲۰۲۴',
                'slug': 'tablet-buying-guide-2024',
                'category': 'buying-guide',
                'excerpt': 'کدام تبلت برای شما مناسب است؟',
                'content': 'تبلت‌ها در سال‌های اخیر پیشرفت زیادی داشته‌اند...',
                'tags': ['تبلت', 'خرید', 'راهنما'], 'is_published': False, 'is_featured': False,
            },
            {
                'title': 'بررسی سونی WH-1000XM5',
                'slug': 'sony-wh1000xm5-review',
                'category': 'technology',
                'excerpt': 'بهترین هدفون نویز کنسلینگ در تست واقعی',
                'content': 'سونی WH-1000XM5 از اولین لحظه‌ای که آن را از جعبه بیرون می‌آورید...',
                'tags': ['هدفون', 'سونی', 'بررسی'], 'is_published': True, 'is_featured': True,
            },
            {
                'title': 'آموزش تنظیم خانه هوشمند با الکسا',
                'slug': 'smart-home-alexa-setup',
                'category': 'tutorial',
                'excerpt': 'گام به گام خانه‌ات را هوشمند کن',
                'content': 'در این آموزش یاد می‌گیریم چطور با استفاده از الکسا...',
                'tags': ['خانه هوشمند', 'الکسا', 'آموزش'], 'is_published': True, 'is_featured': False,
            },
        ]

        for pd in posts:
            if not BlogPost.objects.filter(slug=pd['slug']).exists():
                cat = self.blog_cats.get(pd['category'])
                color = random.choice(COLORS)
                img = _make_image(color, (800, 450), f"blog_{pd['slug']}.jpg")
                post = BlogPost(
                    title=pd['title'],
                    slug=pd['slug'],
                    excerpt=pd['excerpt'],
                    content=pd['content'],
                    category=cat,
                    tags=pd['tags'],
                    is_published=pd['is_published'],
                    is_featured=pd['is_featured'],
                    is_active=True,
                    author_name='تیم بست',
                    read_time=f"{random.randint(3, 12)} دقیقه",
                )
                if pd['is_published']:
                    post.published_at = timezone.now()
                post.save()
                if img:
                    post.image.save(f"blog_{pd['slug']}.jpg", img, save=True)

        self.stdout.write('  ✔ بلاگ و مقالات ساخته شدند')

    # ─── Banners ─────────────────────────────────────────────────────────────

    def _create_banners(self):
        from banners.models import Banner
        import datetime

        banners = [
            {
                'banner_type': 'discount_main', 'title': 'حراج ویژه تابستان', 'order': 1,
                'subtitle': 'تا ۳۰٪ تخفیف روی محصولات منتخب',
                'link': '/products?sale=true', 'button_text': 'خرید کنید',
                'color': (220, 60, 60),
            },
            {
                'banner_type': 'single', 'title': 'جدیدترین گوشی‌های سامسونگ', 'order': 2,
                'subtitle': 'Galaxy S24 Ultra اکنون موجود است',
                'link': '/products/samsung-galaxy-s24-ultra', 'button_text': 'مشاهده محصول',
                'color': (40, 120, 200),
            },
            {
                'banner_type': 'single', 'title': 'لپ‌تاپ‌های پریمیوم', 'order': 3,
                'subtitle': 'برترین لپ‌تاپ‌ها با بهترین قیمت',
                'link': '/products?category=laptops', 'button_text': 'بیشتر ببینید',
                'color': (60, 160, 80),
            },
            {
                'banner_type': 'double', 'title': 'هدفون‌های حرفه‌ای', 'order': 4,
                'subtitle': 'صدای بی‌نظیر در هر محیطی',
                'link': '/products?category=headphones-earphones', 'button_text': 'خرید',
                'color': (160, 60, 200),
            },
            {
                'banner_type': 'double', 'title': 'خانه هوشمند', 'order': 5,
                'subtitle': 'زندگی آسان‌تر با فناوری',
                'link': '/products?category=smart-home', 'button_text': 'کشف کنید',
                'color': (200, 140, 40),
            },
            {
                'banner_type': 'footer_main', 'title': 'اپلیکیشن بست را دانلود کنید', 'order': 6,
                'subtitle': 'تجربه خرید بهتر با اپ موبایل',
                'link': '/app', 'button_text': 'دانلود',
                'color': (40, 140, 160),
            },
        ]

        for b in banners:
            if not Banner.objects.filter(banner_type=b['banner_type'], title=b['title']).exists():
                banner = Banner(
                    banner_type=b['banner_type'],
                    title=b['title'],
                    subtitle=b['subtitle'],
                    link=b['link'],
                    button_text=b['button_text'],
                    is_active=True,
                    order=b['order'],
                )
                img = _make_image(b['color'], (1200, 400), f"banner_{b['order']}.jpg")
                if img:
                    banner.image.save(f"banner_{b['order']}.jpg", img, save=False)
                banner.save()

        self.stdout.write('  ✔ بنرها ساخته شدند')

    # ─── Sliders ─────────────────────────────────────────────────────────────

    def _create_sliders(self):
        from slider.models import Slider

        sliders = [
            {
                'title': 'Galaxy S24 Ultra', 'order': 1,
                'subtitle': 'تجربه‌ای متفاوت از فلگشیپ',
                'description': 'با دوربین ۲۰۰ مگاپیکسلی و قلم S Pen یکپارچه',
                'cta_text': 'همین الان بخرید', 'cta_link': '/products/samsung-galaxy-s24-ultra',
                'category': 'موبایل', 'color': (30, 30, 60),
            },
            {
                'title': 'آیفون ۱۵ پرو مکس', 'order': 2,
                'subtitle': 'فناوری تیتانیوم، قدرت A17 Pro',
                'description': 'پرقدرت‌ترین آیفون تاریخ با بدنه تیتانیوم',
                'cta_text': 'مشاهده محصول', 'cta_link': '/products/apple-iphone-15-pro-max',
                'category': 'موبایل', 'color': (180, 160, 120),
            },
            {
                'title': 'لپ‌تاپ OLED جدید', 'order': 3,
                'subtitle': 'صفحه نمایش خیره‌کننده برای هر کاری',
                'description': 'ایسوس ZenBook 14 OLED با وزن کمتر از 1.4 کیلوگرم',
                'cta_text': 'اطلاعات بیشتر', 'cta_link': '/products/asus-zenbook-14-oled',
                'category': 'لپ‌تاپ', 'color': (20, 80, 140),
            },
            {
                'title': 'حراج ویژه تابستان', 'order': 4,
                'subtitle': 'تا ۳۰٪ تخفیف روی محصولات منتخب',
                'description': 'فرصت را از دست ندهید! پیشنهادات محدود',
                'cta_text': 'مشاهده تخفیف‌ها', 'cta_link': '/products?sale=true',
                'category': 'ویژه', 'color': (180, 60, 40),
            },
        ]

        for s in sliders:
            if not Slider.objects.filter(title=s['title']).exists():
                slider = Slider(
                    title=s['title'],
                    subtitle=s['subtitle'],
                    description=s['description'],
                    cta_text=s['cta_text'],
                    cta_link=s['cta_link'],
                    category=s['category'],
                    order=s['order'],
                    is_active=True,
                )
                img = _make_image(s['color'], (1400, 600), f"slider_{s['order']}.jpg")
                if img:
                    slider.image.save(f"slider_{s['order']}.jpg", img, save=False)
                slider.save()

        self.stdout.write('  ✔ اسلایدرها ساخته شدند')

    # ─── FAQ ─────────────────────────────────────────────────────────────────

    def _create_faq(self):
        from faq.models import FAQCategory, FAQ

        faq_data = [
            {
                'name': 'سوالات خرید', 'icon': 'shopping-cart', 'order': 1,
                'faqs': [
                    ('چطور می‌توانم سفارش دهم؟', 'محصول مورد نظر را انتخاب کرده، به سبد خرید اضافه کنید و مراحل پرداخت را طی کنید.'),
                    ('آیا می‌توانم سفارش خود را لغو کنم؟', 'تا قبل از ارسال، از طریق پروفایل خود می‌توانید سفارش را لغو کنید.'),
                    ('چه روش‌های پرداختی پشتیبانی می‌شود؟', 'پرداخت آنلاین با تمام درگاه‌های بانکی و همچنین پرداخت درب منزل.'),
                    ('آیا امکان خرید اقساطی وجود دارد؟', 'بله، برای برخی محصولات خرید اقساطی از طریق بانک‌های طرف قرارداد امکان‌پذیر است.'),
                ]
            },
            {
                'name': 'ارسال و تحویل', 'icon': 'truck', 'order': 2,
                'faqs': [
                    ('مدت زمان ارسال چقدر است؟', 'معمولاً ۲ تا ۵ روز کاری پس از تأیید سفارش.'),
                    ('هزینه ارسال چقدر است؟', 'برای سفارش‌های بالای ۵۰۰ هزار تومان ارسال رایگان است.'),
                    ('آیا ارسال فوری دارید؟', 'بله، در برخی شهرها ارسال همان روز یا فردا موجود است.'),
                ]
            },
            {
                'name': 'گارانتی و مرجوعی', 'icon': 'shield', 'order': 3,
                'faqs': [
                    ('شرایط مرجوعی کالا چیست؟', 'کالا باید تا ۷ روز از تاریخ تحویل، در صورت داشتن ایراد، مرجوع شود.'),
                    ('گارانتی محصولات چقدر است؟', 'گارانتی محصولات متفاوت است و در صفحه هر محصول ذکر شده.'),
                    ('اگر کالا معیوب باشد چه کار کنم؟', 'با پشتیبانی تماس بگیرید تا فرایند تعویض یا تعمیر آغاز شود.'),
                ]
            },
            {
                'name': 'کیف پول و تخفیف', 'icon': 'wallet', 'order': 4,
                'faqs': [
                    ('کیف پول دیجیتال چیست؟', 'کیف پول دیجیتال امکان شارژ اعتبار و استفاده در خریدهای بعدی را می‌دهد.'),
                    ('چطور کد تخفیف استفاده کنم؟', 'در مرحله نهایی سبد خرید، کد تخفیف را وارد کنید.'),
                    ('آیا می‌توانم چند کد تخفیف ترکیب کنم؟', 'در هر سفارش فقط یک کد تخفیف قابل استفاده است.'),
                ]
            },
        ]

        for cat_data in faq_data:
            cat, _ = FAQCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'icon': cat_data['icon'], 'order': cat_data['order']}
            )
            for j, (question, answer) in enumerate(cat_data['faqs']):
                FAQ.objects.get_or_create(
                    question=question,
                    defaults={
                        'answer': answer,
                        'category': cat,
                        'is_active': True,
                        'order': j,
                    }
                )

        self.stdout.write('  ✔ دسته‌بندی‌ها و سوالات متداول ساخته شدند')

    # ─── Discounts ───────────────────────────────────────────────────────────

    def _create_discounts(self):
        from discounts.models import DiscountCode, GiftCard
        import datetime

        discounts = [
            {
                'code': 'WELCOME20', 'discount_type': 'percent', 'discount_value': 20,
                'min_cart_total': 500000, 'max_discount': 500000,
                'usage_limit': 1000, 'is_active': True,
                'expires_at': (timezone.now() + timezone.timedelta(days=90)).date(),
            },
            {
                'code': 'SAVE50K', 'discount_type': 'fixed', 'discount_value': 50000,
                'min_cart_total': 300000, 'max_discount': None,
                'usage_limit': 500, 'is_active': True,
                'expires_at': (timezone.now() + timezone.timedelta(days=60)).date(),
            },
            {
                'code': 'VIP30', 'discount_type': 'percent', 'discount_value': 30,
                'min_cart_total': 1000000, 'max_discount': 2000000,
                'usage_limit': 100, 'is_active': True,
                'expires_at': (timezone.now() + timezone.timedelta(days=30)).date(),
            },
        ]

        for d in discounts:
            dtype = 'percent' if d['discount_type'] == 'percent' else 'fixed'
            DiscountCode.objects.get_or_create(
                code=d['code'],
                defaults={
                    'discount_type': dtype,
                    'discount_value': d['discount_value'],
                    'min_cart_total': d['min_cart_total'],
                    'max_discount': d['max_discount'],
                    'usage_limit': d['usage_limit'],
                    'is_active': d['is_active'],
                    'expires_at': d['expires_at'],
                }
            )

        gifts = [
            {'code': 'GIFT100K', 'balance': 100000, 'is_active': True,
             'expires_at': (timezone.now() + timezone.timedelta(days=180)).date()},
            {'code': 'GIFT200K', 'balance': 200000, 'is_active': True,
             'expires_at': (timezone.now() + timezone.timedelta(days=180)).date()},
        ]
        for g in gifts:
            GiftCard.objects.get_or_create(
                code=g['code'],
                defaults={
                    'balance': g['balance'],
                    'is_active': g['is_active'],
                    'expires_at': g['expires_at'],
                }
            )

        self.stdout.write('  ✔ کدهای تخفیف و گیفت کارت ساخته شدند')
