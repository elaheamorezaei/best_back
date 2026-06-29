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

        self.stdout.write('>>> Starting seed...')
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
        self.stdout.write(self.style.SUCCESS('>>> Seed completed successfully!'))

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

        self.stdout.write('--- Clearing existing data...')
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
            self.stdout.write(f'  [OK] Admin created: {email} / Admin@1234')
        else:
            self.stdout.write(f'  [--] Admin already exists: {email}')

    def _create_users(self):
        from users.models import UserProfile
        users_data = [
            {'username': 'user1', 'email': 'user1@test.com', 'password': 'Test@1234',
             'first_name': 'علی', 'last_name': 'احمدی',
             'phone': '09111111111',
             'full_name': 'علی احمدی',
             'gender': 'آقا'},
            {'username': 'user2', 'email': 'user2@test.com', 'password': 'Test@1234',
             'first_name': 'مریم', 'last_name': 'رضایی',
             'phone': '09222222222',
             'full_name': 'مریم رضایی',
             'gender': 'خانم'},
            {'username': 'user3', 'email': 'user3@test.com', 'password': 'Test@1234',
             'first_name': 'رضا', 'last_name': 'محمدی',
             'phone': '09333333333',
             'full_name': 'رضا محمدی',
             'gender': 'آقا'},
        ]
        count = 0
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
                count += 1
        self.stdout.write(f'  [OK] Users created: {count}')

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
        total = 0
        for pname, cities in provinces.items():
            p, _ = Province.objects.get_or_create(name=pname)
            for cname in cities:
                _, created = City.objects.get_or_create(province=p, name=cname)
                if created:
                    total += 1
        self.stdout.write(f'  [OK] Provinces and cities created')

    # ─── Delivery Slots ───────────────────────────────────────────────────────

    def _create_delivery_slots(self):
        from delivery.models import DeliveryTimeSlot
        import datetime
        slots = [
            ('صبح (8-12)', datetime.time(8, 0), datetime.time(12, 0)),
            ('ظهر (12-16)', datetime.time(12, 0), datetime.time(16, 0)),
            ('عصر (16-20)', datetime.time(16, 0), datetime.time(20, 0)),
        ]
        for label, from_t, to_t in slots:
            DeliveryTimeSlot.objects.get_or_create(
                label=label,
                defaults={'from_time': from_t, 'to_time': to_t, 'is_active': True}
            )
        self.stdout.write('  [OK] Delivery slots created')

    # ─── Categories ──────────────────────────────────────────────────────────

    def _create_categories(self):
        from products.models import Category
        main_cats = [
            {'name': 'موبایل و تبلت',
             'slug': 'mobile-tablet', 'icon': 'smartphone', 'order': 1,
             'desc': 'انواع گوشی‌های هوشمند، تبلت و لوازم جانبی',
             'children': [
                 {'name': 'گوشی موبایل', 'slug': 'mobile-phones', 'order': 1},
                 {'name': 'تبلت', 'slug': 'tablets', 'order': 2},
             ]},
            {'name': 'لپ‌تاپ و کامپیوتر',
             'slug': 'laptop-computer', 'icon': 'laptop', 'order': 2,
             'desc': 'لپ‌تاپ، کامپیوتر و لوازم جانبی',
             'children': [
                 {'name': 'لپ‌تاپ', 'slug': 'laptops', 'order': 1},
                 {'name': 'کامپیوتر رومیزی', 'slug': 'desktop-computers', 'order': 2},
             ]},
            {'name': 'صوتی و تصویری',
             'slug': 'audio-video', 'icon': 'headphones', 'order': 3,
             'desc': 'تلویزیون، هدفون، بلندگو و تجهیزات صوتی-تصویری',
             'children': [
                 {'name': 'هدفون و هندزفری', 'slug': 'headphones-earphones', 'order': 1},
                 {'name': 'بلندگو', 'slug': 'speakers', 'order': 2},
             ]},
            {'name': 'خانه هوشمند',
             'slug': 'smart-home', 'icon': 'home', 'order': 4,
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

        self.stdout.write(f'  [OK] Categories created: {len(self.categories)}')

    # ─── Products ─────────────────────────────────────────────────────────────

    def _create_products(self):
        from products.models import (Product, ProductColor, ProductWarranty,
                                      ProductFeature, ProductSpec,
                                      ProductIntro, ProductEditorialReview)
        products_data = [
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'slug': 'samsung-galaxy-s24-ultra',
                'sku': 'SAM-S24U-001', 'brand': 'Samsung', 'model': 'SM-S928B',
                'category': 'mobile-phones', 'price': 45000000, 'compare_price': 48000000,
                'stock': 25, 'min_stock': 5, 'is_featured': True, 'is_new': True,
                'tags': ['mobile', 'samsung', 'flagship', 'android'],
                'short_desc': 'قدرتمندترین گوشی سامسونگ با دوربین 200 مگاپیکسل',
                'desc': 'Samsung Galaxy S24 Ultra with Snapdragon 8 Gen 3 and 200MP camera.',
                'colors': [
                    ('مشکی تیتانیوم', '#1A1A1A'),
                    ('بژ تیتانیوم', '#C8B8A2'),
                    ('بنفش تیتانیوم', '#7B68EE'),
                ],
                'warranties': [
                    'گارانتی 18 ماهه سامسونگ',
                    'ضمانت اصالت کالا',
                ],
                'features': [
                    ('CPU', 'Snapdragon 8 Gen 3'),
                    ('RAM', '12 GB'),
                    ('Storage', '256 GB'),
                    ('Camera', '200 MP'),
                ],
                'specs': [
                    ('Weight', '232g'),
                    ('Dimensions', '79x162x8.6mm'),
                    ('Battery', '5000 mAh'),
                    ('Charging', '45W'),
                    ('OS', 'Android 14'),
                ],
                'intro': 'Samsung pushes the boundaries of mobile technology with this flagship.',
                'pros': ['Amazing camera', 'Premium design', 'Strong battery'],
                'cons': ['High price', 'Heavy'],
            },
            {
                'name': 'Apple iPhone 15 Pro Max',
                'slug': 'apple-iphone-15-pro-max',
                'sku': 'APL-IP15PM-001', 'brand': 'Apple', 'model': 'A3105',
                'category': 'mobile-phones', 'price': 62000000, 'compare_price': 65000000,
                'stock': 15, 'min_stock': 3, 'is_featured': True, 'is_sale': True,
                'tags': ['iphone', 'apple', 'ios', 'flagship'],
                'short_desc': 'iPhone 15 Pro Max with A17 Pro chip and titanium body.',
                'desc': 'The iPhone 15 Pro Max with A17 Pro chip and titanium build is the best iPhone ever made.',
                'colors': [
                    ('Natural Titanium', '#C4B49A'),
                    ('Black Titanium', '#3D3D3D'),
                    ('White Titanium', '#F0EDE8'),
                ],
                'warranties': [
                    'گارانتی 18 ماهه شرکتی',
                    'Apple Support',
                ],
                'features': [
                    ('Chip', 'A17 Pro'),
                    ('RAM', '8 GB'),
                    ('Storage', '256 GB'),
                    ('Camera', '48 MP'),
                ],
                'specs': [
                    ('Weight', '221g'),
                    ('Dimensions', '77x159.9x8.25mm'),
                    ('Battery', '4422 mAh'),
                    ('Charging', '27W'),
                    ('OS', 'iOS 17'),
                ],
                'intro': 'Apple redefines premium with the iPhone 15 Pro Max.',
                'pros': ['Unmatched performance', 'Titanium build', 'Apple ecosystem'],
                'cons': ['Very expensive', 'No charger included'],
            },
            {
                'name': 'Xiaomi Redmi Note 13 Pro',
                'slug': 'xiaomi-redmi-note-13-pro',
                'sku': 'XMI-RN13P-001', 'brand': 'Xiaomi', 'model': '2312DRA50G',
                'category': 'mobile-phones', 'price': 12500000, 'compare_price': 14000000,
                'stock': 50, 'min_stock': 10, 'is_new': True, 'is_sale': True,
                'tags': ['xiaomi', 'redmi', 'midrange', 'budget'],
                'short_desc': 'Best mid-range phone with 200MP camera.',
                'desc': 'Redmi Note 13 Pro with 200MP camera and AMOLED 120Hz display.',
                'colors': [
                    ('Midnight Black', '#1C2333'),
                    ('Forest Green', '#2D5016'),
                    ('Lavender Purple', '#967BB6'),
                ],
                'warranties': ['گارانتی 12 ماهه'],
                'features': [
                    ('CPU', 'Snapdragon 7s Gen 2'),
                    ('RAM', '8 GB'),
                    ('Storage', '256 GB'),
                    ('Camera', '200 MP'),
                ],
                'specs': [
                    ('Weight', '187g'),
                    ('Dimensions', '74.2x161.1x8mm'),
                    ('Battery', '5000 mAh'),
                    ('Charging', '67W Fast Charge'),
                    ('Display', 'AMOLED 6.67"'),
                ],
                'intro': 'Redmi Note 13 Pro proves you do not need to spend a fortune for a great phone.',
                'pros': ['Good price', 'Excellent camera', 'Fast charging'],
                'cons': ['Mid-range CPU', 'No NFC'],
            },
            {
                'name': 'Apple iPad Pro 12.9 M2',
                'slug': 'apple-ipad-pro-12-9-m2',
                'sku': 'APL-IPDP129-001', 'brand': 'Apple', 'model': 'MNXR3',
                'category': 'tablets', 'price': 38000000, 'compare_price': 40000000,
                'stock': 10, 'min_stock': 2, 'is_featured': True,
                'tags': ['ipad', 'apple', 'tablet', 'pro'],
                'short_desc': 'iPad Pro with M2 chip and Liquid Retina XDR display.',
                'desc': 'The iPad Pro 12.9 with M2 chip is the most powerful tablet available.',
                'colors': [
                    ('Silver', '#C0C0C0'),
                    ('Space Gray', '#4A4A4A'),
                ],
                'warranties': ['گارانتی 18 ماهه اپل'],
                'features': [
                    ('Chip', 'Apple M2'),
                    ('RAM', '8 GB'),
                    ('Storage', '128 GB'),
                    ('Display', '12.9" Liquid Retina XDR'),
                ],
                'specs': [
                    ('Weight', '682g'),
                    ('Dimensions', '280.6x214.9x6.4mm'),
                    ('Battery', '10541 mAh'),
                    ('Connectivity', 'Wi-Fi 6E, 5G'),
                    ('OS', 'iPadOS 17'),
                ],
                'intro': 'The iPad Pro with M2 delivers desktop-class performance in a thin tablet.',
                'pros': ['Best tablet display', 'Incredibly powerful', 'Apple ecosystem'],
                'cons': ['Expensive', 'No USB-A'],
            },
            {
                'name': 'Asus ZenBook 14 OLED',
                'slug': 'asus-zenbook-14-oled',
                'sku': 'ASUS-ZB14-001', 'brand': 'Asus', 'model': 'UX3402VA',
                'category': 'laptops', 'price': 32000000, 'compare_price': 35000000,
                'stock': 8, 'min_stock': 2, 'is_featured': True, 'is_new': True,
                'tags': ['laptop', 'asus', 'oled', 'ultrabook'],
                'short_desc': 'Lightweight laptop with stunning OLED 2.8K display.',
                'desc': 'ZenBook 14 OLED with Core i7 gen 13 and gorgeous OLED screen.',
                'colors': [
                    ('Ponder Blue', '#1E5F8E'),
                    ('Bronzite Brown', '#C4A882'),
                ],
                'warranties': [
                    'گارانتی 18 ماهه ایسوس',
                    'پشتیبانی فنی 2 ساله',
                ],
                'features': [
                    ('CPU', 'Intel Core i7-1360P'),
                    ('RAM', '16 GB LPDDR5'),
                    ('Storage', '512 GB NVMe SSD'),
                    ('Display', 'OLED 2.8K 90Hz'),
                ],
                'specs': [
                    ('Weight', '1.39 kg'),
                    ('Battery', '75Wh'),
                    ('Charging', '65W USB-C'),
                    ('OS', 'Windows 11'),
                    ('Connectivity', 'Wi-Fi 6E, BT 5.3'),
                ],
                'intro': 'Asus proves you can have a portable laptop without compromise.',
                'pros': ['Beautiful OLED screen', 'Lightweight', 'Stylish design'],
                'cons': ['Runs hot under load', 'Limited ports'],
            },
            {
                'name': 'Lenovo ThinkPad X1 Carbon Gen 11',
                'slug': 'lenovo-thinkpad-x1-carbon-gen11',
                'sku': 'LNV-X1CG11-001', 'brand': 'Lenovo', 'model': '21HM0054',
                'category': 'laptops', 'price': 42000000, 'compare_price': 45000000,
                'stock': 5, 'min_stock': 1, 'is_featured': False,
                'tags': ['laptop', 'lenovo', 'thinkpad', 'business'],
                'short_desc': 'Ultra-light business laptop for professionals.',
                'desc': 'ThinkPad X1 Carbon with carbon fiber body and legendary keyboard.',
                'colors': [('Black', '#1A1A1A')],
                'warranties': [
                    'گارانتی 3 ساله لنوو',
                    '24/7 Phone Support',
                ],
                'features': [
                    ('CPU', 'Intel Core i7-1365U'),
                    ('RAM', '16 GB LPDDR5'),
                    ('Storage', '512 GB SSD'),
                    ('Display', '14" IPS 2.8K'),
                ],
                'specs': [
                    ('Weight', '1.12 kg'),
                    ('Battery', '57Wh'),
                    ('Charging', 'Rapid Charge 65W'),
                    ('OS', 'Windows 11 Pro'),
                    ('Connectivity', 'Wi-Fi 6E, LTE optional'),
                ],
                'intro': 'ThinkPad X1 Carbon passes MIL-SPEC durability tests.',
                'pros': ['Ultra lightweight', 'Highly durable', 'Best keyboard'],
                'cons': ['Premium price', 'Weak GPU'],
            },
            {
                'name': 'Sony WH-1000XM5',
                'slug': 'sony-wh-1000xm5',
                'sku': 'SONY-WH1KM5-001', 'brand': 'Sony', 'model': 'WH-1000XM5',
                'category': 'headphones-earphones', 'price': 8500000, 'compare_price': 9500000,
                'stock': 30, 'min_stock': 5, 'is_featured': True, 'is_best_seller': True,
                'tags': ['headphones', 'sony', 'anc', 'bluetooth'],
                'short_desc': 'Best noise-canceling headphones in the world.',
                'desc': 'Sony WH-1000XM5 with advanced ANC and exceptional sound quality.',
                'colors': [('Black', '#1A1A1A'), ('Silver', '#C0C0C0')],
                'warranties': ['گارانتی 18 ماهه سونی'],
                'features': [
                    ('ANC', 'Advanced Active Noise Cancelling'),
                    ('Battery', '30 hours'),
                    ('Connectivity', 'Bluetooth 5.2'),
                    ('Codec', 'LDAC, AAC, SBC'),
                ],
                'specs': [
                    ('Weight', '250g'),
                    ('Driver', '30mm'),
                    ('Frequency', '4Hz - 40kHz'),
                    ('Impedance', '16 Ohm'),
                    ('Charging', 'USB-C 3h'),
                ],
                'intro': 'WH-1000XM5 is the result of years of Sony research into audio and noise cancellation.',
                'pros': ['Best ANC on market', 'Premium sound', 'Comfortable'],
                'cons': ['Expensive', 'Not foldable'],
            },
            {
                'name': 'Apple AirPods Pro 2',
                'slug': 'apple-airpods-pro-2',
                'sku': 'APL-APP2-001', 'brand': 'Apple', 'model': 'MTJV3',
                'category': 'headphones-earphones', 'price': 7800000, 'compare_price': 8500000,
                'stock': 20, 'min_stock': 4, 'is_featured': True, 'is_sale': True,
                'tags': ['airpods', 'apple', 'earbuds', 'tws'],
                'short_desc': 'Apple wireless earbuds with improved ANC.',
                'desc': 'AirPods Pro 2nd gen with 2x stronger ANC and adaptive audio.',
                'colors': [('White', '#F5F5F5')],
                'warranties': ['گارانتی 18 ماهه اپل'],
                'features': [
                    ('Chip', 'Apple H2'),
                    ('ANC', 'Up to 29dB reduction'),
                    ('Battery', '6h + 30h with case'),
                    ('Charging', 'MagSafe, USB-C'),
                ],
                'specs': [
                    ('Weight per earbud', '5.3g'),
                    ('Case weight', '50.8g'),
                    ('Connectivity', 'Bluetooth 5.3'),
                    ('Water resistance', 'IPX4'),
                ],
                'intro': 'AirPods Pro 2 with personalized spatial audio delivers a unique listening experience.',
                'pros': ['Powerful ANC', 'Spatial audio', 'Apple integration'],
                'cons': ['Apple ecosystem only', 'Premium price'],
            },
            {
                'name': 'Bose SoundLink Max',
                'slug': 'bose-soundlink-max',
                'sku': 'BOSE-SLM-001', 'brand': 'Bose', 'model': 'SoundLink Max',
                'category': 'speakers', 'price': 9200000, 'compare_price': 10000000,
                'stock': 15, 'min_stock': 3, 'is_new': True,
                'tags': ['speaker', 'bose', 'wireless', 'portable'],
                'short_desc': 'Biggest and loudest Bose portable speaker.',
                'desc': 'Bose SoundLink Max with powerful sound, waterproof design and 20h battery.',
                'colors': [('Black', '#1A1A1A'), ('Stone Blue', '#4A6FA5')],
                'warranties': ['گارانتی 12 ماهه بوز'],
                'features': [
                    ('Power', '36W'),
                    ('Battery', '20 hours'),
                    ('Connectivity', 'Bluetooth 5.3'),
                    ('Water resistance', 'IP67'),
                ],
                'specs': [
                    ('Weight', '1.3 kg'),
                    ('Dimensions', '243x97x97mm'),
                    ('Charging', 'USB-C'),
                    ('Frequency', '55Hz - 20kHz'),
                ],
                'intro': 'The SoundLink Max uses advanced Bose acoustic technology for powerful, detailed sound.',
                'pros': ['Powerful sound', 'IP67 waterproof', 'Long battery'],
                'cons': ['Heavy', 'Expensive'],
            },
            {
                'name': 'Amazon Echo Dot Gen 5',
                'slug': 'amazon-echo-dot-gen5',
                'sku': 'AMZ-ED5-001', 'brand': 'Amazon', 'model': 'Echo Dot Gen 5',
                'category': 'smart-speakers', 'price': 2800000, 'compare_price': 3200000,
                'stock': 40, 'min_stock': 8, 'is_sale': True, 'is_popular': True,
                'tags': ['smarthome', 'amazon', 'alexa', 'smart-speaker'],
                'short_desc': 'Smart speaker with Alexa voice assistant.',
                'desc': 'Echo Dot Gen 5 with Alexa can make your home smart.',
                'colors': [
                    ('Deep Sea Blue', '#2E86AB'),
                    ('Charcoal', '#1A1A1A'),
                    ('Glacier White', '#F5F5F5'),
                ],
                'warranties': ['گارانتی 12 ماهه'],
                'features': [
                    ('Assistant', 'Amazon Alexa'),
                    ('Speaker', '1.73 inch'),
                    ('Connectivity', 'Wi-Fi 6, Bluetooth 5.0'),
                    ('Feature', 'Smart Home Hub'),
                ],
                'specs': [
                    ('Weight', '304g'),
                    ('Dimensions', '99x99x89mm'),
                    ('Adapter', '15W'),
                    ('Microphones', '4'),
                ],
                'intro': 'Echo Dot is the easiest way to enter the smart home world.',
                'pros': ['Affordable', 'Easy to use', 'Wide integration'],
                'cons': ['Requires internet', 'Privacy concerns'],
            },
            {
                'name': 'Wyze Cam v4',
                'slug': 'wyze-cam-v4',
                'sku': 'WYZE-CAM4-001', 'brand': 'Wyze', 'model': 'Wyze Cam v4',
                'category': 'smart-cameras', 'price': 1500000, 'compare_price': 1800000,
                'stock': 35, 'min_stock': 7, 'is_new': True, 'is_popular': True,
                'tags': ['camera', 'smart', 'security', 'wyze'],
                'short_desc': '2K security camera with color night vision.',
                'desc': 'Wyze Cam v4 with 2K resolution, color night vision and AI motion detection.',
                'colors': [('White', '#F5F5F5')],
                'warranties': ['گارانتی 12 ماهه'],
                'features': [
                    ('Resolution', '2K 2560x1440'),
                    ('Night Vision', 'Color up to 9m'),
                    ('Detection', 'AI Motion'),
                    ('Storage', 'microSD up to 256GB'),
                ],
                'specs': [
                    ('Weight', '113g'),
                    ('Connectivity', 'Wi-Fi 2.4GHz & 5GHz'),
                    ('FOV', '130 degrees'),
                    ('Water resistance', 'IP65'),
                ],
                'intro': 'Wyze Cam v4 proves quality home security does not have to be expensive.',
                'pros': ['Very affordable', '2K quality', 'Easy setup'],
                'cons': ['Subscription for some features', 'Limited free cloud'],
            },
            {
                'name': 'Samsung Galaxy Tab S9 FE',
                'slug': 'samsung-galaxy-tab-s9-fe',
                'sku': 'SAM-TABS9FE-001', 'brand': 'Samsung', 'model': 'SM-X510',
                'category': 'tablets', 'price': 16500000, 'compare_price': 18000000,
                'stock': 12, 'min_stock': 3, 'is_sale': True,
                'tags': ['tablet', 'samsung', 'galaxy', 'android'],
                'short_desc': 'Mid-range Samsung tablet with S Pen included.',
                'desc': 'Galaxy Tab S9 FE with 10.9" TFT display, S Pen and 8000mAh battery.',
                'colors': [
                    ('Gray', '#808080'),
                    ('Lavender', '#967BB6'),
                    ('Mint', '#2E8B57'),
                ],
                'warranties': ['گارانتی 18 ماهه سامسونگ'],
                'features': [
                    ('CPU', 'Exynos 1380'),
                    ('RAM', '6 GB'),
                    ('Storage', '128 GB'),
                    ('S Pen', 'Included'),
                ],
                'specs': [
                    ('Weight', '523g'),
                    ('Display', 'TFT 10.9"'),
                    ('Battery', '8000 mAh'),
                    ('Charging', '45W'),
                    ('OS', 'Android 13'),
                ],
                'intro': 'Galaxy Tab S9 FE is the best choice for those seeking premium Samsung at a reasonable budget.',
                'pros': ['S Pen included free', 'Large display', 'Strong battery'],
                'cons': ['TFT not AMOLED', 'Mid-range CPU'],
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
                        text=f"Editorial review: {pd['name']}",
                        pros=pd.get('pros', []),
                        cons=pd.get('cons', []),
                    )

            self.product_objs.append(p)

        self.stdout.write(f'  [OK] Products created: {len(products_data)}')

    # ─── Blog ─────────────────────────────────────────────────────────────────

    def _create_blog(self):
        from blog.models import BlogCategory, BlogPost

        blog_cats = [
            {'name': 'Technology', 'slug': 'technology', 'icon': 'cpu', 'order': 1},
            {'name': 'Buying Guide', 'slug': 'buying-guide', 'icon': 'shopping-bag', 'order': 2},
            {'name': 'News', 'slug': 'news', 'icon': 'newspaper', 'order': 3},
            {'name': 'Tutorial', 'slug': 'tutorial', 'icon': 'book', 'order': 4},
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
                'title': 'بهترین گوشی‌های 2024',
                'slug': 'best-phones-2024',
                'category': 'buying-guide',
                'excerpt': 'راهنمای جامع خرید گوشی در سال 2024',
                'content': 'در این مقاله به بررسی بهترین گوشی‌های 2024 می‌پردازیم...',
                'tags': ['phone', 'buying', '2024'], 'is_published': True, 'is_featured': True,
            },
            {
                'title': 'مقایسه iPhone 15 Pro Max با Galaxy S24 Ultra',
                'slug': 'iphone-15-vs-galaxy-s24',
                'category': 'technology',
                'excerpt': 'کدام فلگشیپ ارزش خریدن دارد؟',
                'content': 'آیفون یا سامسونگ؟...',
                'tags': ['iphone', 'samsung', 'comparison'], 'is_published': True, 'is_featured': False,
            },
            {
                'title': 'جدیدترین لپ‌تاپ‌های 2024',
                'slug': 'new-laptops-2024',
                'category': 'news',
                'excerpt': 'آشنایی با لپ‌تاپ‌هایی که امسال معرفی شدند',
                'content': 'سال 2024 سالی پر از معرفی لپ‌تاپ‌های جذاب بود...',
                'tags': ['laptop', 'news', '2024'], 'is_published': True, 'is_featured': True,
            },
            {
                'title': 'چگونه هدفون مناسب انتخاب کنیم؟',
                'slug': 'how-to-choose-headphones',
                'category': 'tutorial',
                'excerpt': 'راهنمای انتخاب هدفون مناسب',
                'content': 'انتخاب هدفون مناسب می‌تواند گیج‌کننده باشد...',
                'tags': ['headphones', 'tutorial', 'guide'], 'is_published': True, 'is_featured': False,
            },
            {
                'title': 'تکنولوژی OLED چیست؟',
                'slug': 'what-is-oled',
                'category': 'technology',
                'excerpt': 'آشنایی با فناوری OLED',
                'content': 'OLED stands for Organic Light-Emitting Diode...',
                'tags': ['oled', 'display', 'tech'], 'is_published': True, 'is_featured': False,
            },
            {
                'title': 'راهنمای خرید تبلت 2024',
                'slug': 'tablet-buying-guide-2024',
                'category': 'buying-guide',
                'excerpt': 'کدام تبلت برای شما مناسب است؟',
                'content': 'تبلت‌ها در سال‌های اخیر پیشرفت زیادی داشته‌اند...',
                'tags': ['tablet', 'buying', 'guide'], 'is_published': False, 'is_featured': False,
            },
            {
                'title': 'بررسی Sony WH-1000XM5',
                'slug': 'sony-wh1000xm5-review',
                'category': 'technology',
                'excerpt': 'بهترین هدفون نویز کنسلینگ در تست واقعی',
                'content': 'Sony WH-1000XM5 impresses from the first moment...',
                'tags': ['headphones', 'sony', 'review'], 'is_published': True, 'is_featured': True,
            },
            {
                'title': 'آموزش تنظیم خانه هوشمند با الکسا',
                'slug': 'smart-home-alexa-setup',
                'category': 'tutorial',
                'excerpt': 'گام به گام خانه‌ات را هوشمند کن',
                'content': 'در این آموزش یاد می‌گیریم چطور با استفاده از الکسا...',
                'tags': ['smarthome', 'alexa', 'tutorial'], 'is_published': True, 'is_featured': False,
            },
        ]

        count = 0
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
                    author_name='Best Team',
                    read_time=f"{random.randint(3, 12)} min",
                )
                if pd['is_published']:
                    post.published_at = timezone.now()
                post.save()
                if img:
                    post.image.save(f"blog_{pd['slug']}.jpg", img, save=True)
                count += 1

        self.stdout.write(f'  [OK] Blog posts created: {count}')

    # ─── Banners ─────────────────────────────────────────────────────────────

    def _create_banners(self):
        from banners.models import Banner

        banners = [
            {
                'banner_type': 'discount_main', 'order': 1,
                'title': 'حراج ویژه تابستان',
                'subtitle': 'تا 30٪ تخفیف روی محصولات منتخب',
                'link': '/products?sale=true',
                'button_text': 'خرید کنید',
                'color': (220, 60, 60),
            },
            {
                'banner_type': 'single', 'order': 2,
                'title': 'جدیدترین گوشی‌های سامسونگ',
                'subtitle': 'Galaxy S24 Ultra اکنون موجود است',
                'link': '/products/samsung-galaxy-s24-ultra',
                'button_text': 'مشاهده محصول',
                'color': (40, 120, 200),
            },
            {
                'banner_type': 'single', 'order': 3,
                'title': 'لپ‌تاپ‌های پریمیوم',
                'subtitle': 'برترین لپ‌تاپ‌ها با بهترین قیمت',
                'link': '/products?category=laptops',
                'button_text': 'بیشتر ببینید',
                'color': (60, 160, 80),
            },
            {
                'banner_type': 'double', 'order': 4,
                'title': 'هدفون‌های حرفه‌ای',
                'subtitle': 'صدای بی‌نظیر در هر محیطی',
                'link': '/products?category=headphones-earphones',
                'button_text': 'خرید',
                'color': (160, 60, 200),
            },
            {
                'banner_type': 'double', 'order': 5,
                'title': 'خانه هوشمند',
                'subtitle': 'زندگی آسان‌تر با فناوری',
                'link': '/products?category=smart-home',
                'button_text': 'کشف کنید',
                'color': (200, 140, 40),
            },
            {
                'banner_type': 'footer_main', 'order': 6,
                'title': 'اپلیکیشن بست را دانلود کنید',
                'subtitle': 'تجربه خرید بهتر با اپ موبایل',
                'link': '/app',
                'button_text': 'دانلود',
                'color': (40, 140, 160),
            },
        ]

        count = 0
        for b in banners:
            if not Banner.objects.filter(banner_type=b['banner_type'], order=b['order']).exists():
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
                count += 1

        self.stdout.write(f'  [OK] Banners created: {count}')

    # ─── Sliders ─────────────────────────────────────────────────────────────

    def _create_sliders(self):
        from slider.models import Slider

        sliders = [
            {
                'title': 'Galaxy S24 Ultra', 'order': 1,
                'subtitle': 'تجربه‌ای متفاوت از فلگشیپ',
                'description': 'با دوربین 200 مگاپیکسلی و قلم S Pen یکپارچه',
                'cta_text': 'همین الان بخرید',
                'cta_link': '/products/samsung-galaxy-s24-ultra',
                'category': 'موبایل', 'color': (30, 30, 60),
            },
            {
                'title': 'iPhone 15 Pro Max', 'order': 2,
                'subtitle': 'فناوری تیتانیوم، قدرت A17 Pro',
                'description': 'پرقدرت‌ترین آیفون تاریخ با بدنه تیتانیوم',
                'cta_text': 'مشاهده محصول',
                'cta_link': '/products/apple-iphone-15-pro-max',
                'category': 'موبایل', 'color': (180, 160, 120),
            },
            {
                'title': 'ZenBook 14 OLED', 'order': 3,
                'subtitle': 'صفحه نمایش خیره‌کننده برای هر کاری',
                'description': 'وزن کمتر از 1.4 کیلوگرم',
                'cta_text': 'اطلاعات بیشتر',
                'cta_link': '/products/asus-zenbook-14-oled',
                'category': 'لپ‌تاپ', 'color': (20, 80, 140),
            },
            {
                'title': 'حراج ویژه تابستان', 'order': 4,
                'subtitle': 'تا 30٪ تخفیف روی محصولات منتخب',
                'description': 'فرصت را از دست ندهید! پیشنهادات محدود',
                'cta_text': 'مشاهده تخفیف‌ها',
                'cta_link': '/products?sale=true',
                'category': 'ویژه', 'color': (180, 60, 40),
            },
        ]

        count = 0
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
                count += 1

        self.stdout.write(f'  [OK] Sliders created: {count}')

    # ─── FAQ ─────────────────────────────────────────────────────────────────

    def _create_faq(self):
        from faq.models import FAQCategory, FAQ

        faq_data = [
            {
                'name': 'سوالات خرید',
                'icon': 'shopping-cart', 'order': 1,
                'faqs': [
                    ('چطور می‌توانم سفارش دهم؟',
                     'محصول مورد نظر را انتخاب کرده، به سبد خرید اضافه کنید و مراحل پرداخت را طی کنید.'),
                    ('آیا می‌توانم سفارش خود را لغو کنم؟',
                     'تا قبل از ارسال، از طریق پروفایل خود می‌توانید سفارش را لغو کنید.'),
                    ('چه روش‌های پرداختی پشتیبانی می‌شود؟',
                     'پرداخت آنلاین با تمام درگاه‌های بانکی و همچنین پرداخت درب منزل.'),
                    ('آیا امکان خرید اقساطی وجود دارد؟',
                     'بله، برای برخی محصولات خرید اقساطی از طریق بانک‌های طرف قرارداد امکان‌پذیر است.'),
                ]
            },
            {
                'name': 'ارسال و تحویل',
                'icon': 'truck', 'order': 2,
                'faqs': [
                    ('مدت زمان ارسال چقدر است؟',
                     'معمولاً 2 تا 5 روز کاری پس از تأیید سفارش.'),
                    ('هزینه ارسال چقدر است؟',
                     'برای سفارش‌های بالای 500 هزار تومان ارسال رایگان است.'),
                    ('آیا ارسال فوری دارید؟',
                     'بله، در برخی شهرها ارسال همان روز یا فردا موجود است.'),
                ]
            },
            {
                'name': 'گارانتی و مرجوعی',
                'icon': 'shield', 'order': 3,
                'faqs': [
                    ('شرایط مرجوعی کالا چیست؟',
                     'کالا باید تا 7 روز از تاریخ تحویل، در صورت داشتن ایراد، مرجوع شود.'),
                    ('گارانتی محصولات چقدر است؟',
                     'گارانتی محصولات متفاوت است و در صفحه هر محصول ذکر شده.'),
                    ('اگر کالا معیوب باشد چه کار کنم؟',
                     'با پشتیبانی تماس بگیرید تا فرایند تعویض یا تعمیر آغاز شود.'),
                ]
            },
            {
                'name': 'کیف پول و تخفیف',
                'icon': 'wallet', 'order': 4,
                'faqs': [
                    ('کیف پول دیجیتال چیست؟',
                     'کیف پول دیجیتال امکان شارژ اعتبار و استفاده در خریدهای بعدی را می‌دهد.'),
                    ('چطور کد تخفیف استفاده کنم؟',
                     'در مرحله نهایی سبد خرید، کد تخفیف را وارد کنید.'),
                    ('آیا می‌توانم چند کد تخفیف ترکیب کنم؟',
                     'در هر سفارش فقط یک کد تخفیف قابل استفاده است.'),
                ]
            },
        ]

        count = 0
        for cat_data in faq_data:
            cat, _ = FAQCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'icon': cat_data['icon'], 'order': cat_data['order']}
            )
            for j, (question, answer) in enumerate(cat_data['faqs']):
                _, created = FAQ.objects.get_or_create(
                    question=question,
                    defaults={
                        'answer': answer,
                        'category': cat,
                        'is_active': True,
                        'order': j,
                    }
                )
                if created:
                    count += 1

        self.stdout.write(f'  [OK] FAQs created: {count}')

    # ─── Discounts ───────────────────────────────────────────────────────────

    def _create_discounts(self):
        from discounts.models import DiscountCode, GiftCard

        discounts = [
            {
                'code': 'WELCOME20', 'discount_type': DiscountCode.TYPE_PERCENT,
                'discount_value': 20, 'min_cart_total': 500000,
                'max_discount': 500000, 'usage_limit': 1000, 'is_active': True,
                'expires_at': (timezone.now() + timezone.timedelta(days=90)).date(),
            },
            {
                'code': 'SAVE50K', 'discount_type': DiscountCode.TYPE_FIXED,
                'discount_value': 50000, 'min_cart_total': 300000,
                'max_discount': None, 'usage_limit': 500, 'is_active': True,
                'expires_at': (timezone.now() + timezone.timedelta(days=60)).date(),
            },
            {
                'code': 'VIP30', 'discount_type': DiscountCode.TYPE_PERCENT,
                'discount_value': 30, 'min_cart_total': 1000000,
                'max_discount': 2000000, 'usage_limit': 100, 'is_active': True,
                'expires_at': (timezone.now() + timezone.timedelta(days=30)).date(),
            },
        ]

        dc_count = 0
        for d in discounts:
            _, created = DiscountCode.objects.get_or_create(
                code=d['code'],
                defaults={
                    'discount_type': d['discount_type'],
                    'discount_value': d['discount_value'],
                    'min_cart_total': d['min_cart_total'],
                    'max_discount': d['max_discount'],
                    'usage_limit': d['usage_limit'],
                    'is_active': d['is_active'],
                    'expires_at': d['expires_at'],
                }
            )
            if created:
                dc_count += 1

        gifts = [
            {'code': 'GIFT100K', 'balance': 100000, 'is_active': True,
             'expires_at': (timezone.now() + timezone.timedelta(days=180)).date()},
            {'code': 'GIFT200K', 'balance': 200000, 'is_active': True,
             'expires_at': (timezone.now() + timezone.timedelta(days=180)).date()},
        ]
        gc_count = 0
        for g in gifts:
            _, created = GiftCard.objects.get_or_create(
                code=g['code'],
                defaults={
                    'balance': g['balance'],
                    'is_active': g['is_active'],
                    'expires_at': g['expires_at'],
                }
            )
            if created:
                gc_count += 1

        self.stdout.write(f'  [OK] Discount codes: {dc_count}, Gift cards: {gc_count}')
