# API Documentation — My Shop Backend

> **Base URL:** `http://127.0.0.1:8000`
> **API Prefix:** `/api/v1/`
> **Encoding:** UTF-8 / JSON
> **تصاویر:** آدرس کامل در response برگردانده می‌شه (absolute URL)

---

## فهرست مطالب

- [فرمت Response ها](#فرمت-response-ها)
- [احراز هویت (Auth)](#احراز-هویت-auth)
- [صفحه اصلی (Homepage)](#صفحه-اصلی-homepage)
- [صفحه محصول (Product Page)](#صفحه-محصول-product-page)
- [جدول کلی Endpoint ها](#جدول-کلی-endpoint-ها)
- [نکات مهم برای فرانت](#نکات-مهم-برای-فرانت)

---

## فرمت Response ها

### موفقیت — صفحه اصلی
```json
{
  "success": true,
  "data": { ... }
}
```

### موفقیت — صفحه محصول
```json
{
  "data": { ... },
  "message": "پیام اختیاری"
}
```

### خطا (همه endpoint ها)
```json
{
  "error": {
    "code": 400,
    "message": "توضیح خطا",
    "field": "نام فیلد (اختیاری، فقط برای validation error)"
  }
}
```

### کدهای HTTP رایج
| کد | معنی |
|----|------|
| 200 | موفق |
| 201 | ایجاد شد |
| 400 | ورودی نامعتبر |
| 401 | توکن ندارید یا منقضی شده |
| 403 | دسترسی ندارید |
| 404 | آیتم پیدا نشد |

---

## احراز هویت (Auth)

### دریافت توکن
```
POST /api/token/
```

**Request Body:**
```json
{
  "username": "user123",
  "password": "pass123"
}
```

**Response `200`:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

> **access token** مدت اعتبار: **۶۰ دقیقه**
> **refresh token** مدت اعتبار: **۷ روز**

**خطا `401`:**
```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### تمدید توکن
```
POST /api/token/refresh/
```

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `200`:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### نحوه ارسال توکن در Request

برای همه endpoint هایی که نیاز به auth دارن:

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## صفحه اصلی (Homepage)

> همه endpoint های این بخش **بدون auth** قابل دسترسی هستند.

---

### 1. اسلایدر
```
GET /api/v1/slider/
```

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "تخفیف ویژه تابستان",
      "subtitle": "تا ۵۰٪ تخفیف",
      "description": "توضیحات اسلایدر",
      "image": "http://127.0.0.1:8000/media/slider/img.jpg",
      "cta_text": "خرید کنید",
      "cta_link": "/products",
      "category": "electronics"
    }
  ]
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `id` | integer | شناسه |
| `title` | string | عنوان اصلی |
| `subtitle` | string | زیرعنوان |
| `description` | string | توضیحات |
| `image` | string \| null | آدرس کامل تصویر |
| `cta_text` | string | متن دکمه |
| `cta_link` | string | لینک دکمه |
| `category` | string | دسته‌بندی مرتبط |

---

### 2. مگا منو / هدر
```
GET /api/v1/header/mega-menu/
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "mega_menu": {
      "electronics": {
        "id": 1,
        "name": "الکترونیک",
        "slug": "electronics",
        "icon": "laptop",
        "image": "http://127.0.0.1:8000/media/categories/img.jpg",
        "link": "/category/electronics",
        "children": [
          {
            "id": 5,
            "name": "لپ‌تاپ",
            "slug": "laptop",
            "icon": "",
            "image": null,
            "link": "/category/laptop",
            "children": []
          }
        ]
      }
    },
    "categories_list": [
      {
        "id": 1,
        "name": "الکترونیک",
        "slug": "electronics",
        "icon": "laptop"
      }
    ],
    "header_items": [
      {
        "id": 1,
        "name": "پیشنهاد ویژه",
        "link": "/special",
        "icon": "fire"
      }
    ]
  }
}
```

| فیلد | توضیح |
|------|-------|
| `mega_menu` | دیکشنری کلید‌دار با slug دسته‌بندی — برای رندر منوی کشویی |
| `categories_list` | لیست ساده دسته‌بندی‌های سطح اول — برای نوار ناوبری |
| `header_items` | آیتم‌های اضافه هدر (مثل «پیشنهاد ویژه») |

---

### 3. جستجوهای پرتکرار
```
GET /api/v1/search/trending/
```

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "title": "گوشی سامسونگ",
      "link": "/search?q=گوشی+سامسونگ"
    }
  ]
}
```

---

### 4. پیشنهاد جستجو (Autocomplete)
```
GET /api/v1/search/autocomplete/?q={query}
```

**Query Params:**
| پارامتر | نوع | اجباری | توضیح |
|---------|-----|--------|-------|
| `q` | string | بله | حداقل ۲ کاراکتر |

**Response `200`:**
```json
{
  "success": true,
  "query": "صندلی",
  "data": [
    {
      "name": "صندلی کارمندی کرکره ای",
      "category": "مبلمان",
      "link": "/product/1"
    }
  ]
}
```

**خطا `400` — کمتر از ۲ کاراکتر:**
```json
{
  "error": {
    "code": 400,
    "message": "Search term must be at least 2 characters"
  }
}
```

---

### 5. بنر تخفیف اصلی
```
GET /api/v1/banners/discount-main/
```

**Response `200` — وقتی بنر فعال وجود دارد:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "image_url": "http://127.0.0.1:8000/media/banners/img.jpg",
    "alt_text": "تخفیف ویژه",
    "link": "/sale",
    "expires_at": "2026-07-01"
  }
}
```

**Response `200` — وقتی بنری تنظیم نشده:**
```json
{
  "success": true,
  "data": null
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `image_url` | string | آدرس کامل تصویر |
| `alt_text` | string | توضیح تصویر |
| `link` | string | مقصد کلیک |
| `expires_at` | string \| null | تاریخ انقضا (YYYY-MM-DD) |

---

### 6. بنر تکی
```
GET /api/v1/banners/single/
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "image_url": "http://127.0.0.1:8000/media/banners/img.jpg",
    "link": "/category/electronics"
  }
}
```

> وقتی بنری تنظیم نشده: `"data": null`

---

### 7. بنر دوتایی
```
GET /api/v1/banners/double/
```

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "image_url": "http://127.0.0.1:8000/media/banners/img1.jpg",
      "link": "/offer1"
    },
    {
      "id": 4,
      "image_url": "http://127.0.0.1:8000/media/banners/img2.jpg",
      "link": "/offer2"
    }
  ]
}
```

> وقتی بنری تنظیم نشده: `"data": []`

---

### 8. بنر فوتر
```
GET /api/v1/banners/footer-main/
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "image_url": "http://127.0.0.1:8000/media/banners/footer.jpg",
    "link": "/special-offer"
  }
}
```

> وقتی بنری تنظیم نشده: `"data": null`

---

### 9. دسته‌بندی‌های اصلی
```
GET /api/v1/categories/main/
```

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "image": "http://127.0.0.1:8000/media/categories/img.jpg",
      "category": "الکترونیک",
      "link": "/category/electronics"
    }
  ]
}
```

> فیلد اسم دسته‌بندی **`category`** است (نه `name`).

---

### 10. محصولات ویژه
```
GET /api/v1/products/featured/
```

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "image": "http://127.0.0.1:8000/media/products/img.jpg",
      "name": "صندلی کارمندی",
      "model": "A200",
      "star": 4.5,
      "price": 7000000,
      "off": 10,
      "final_price": 6300000
    }
  ]
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `price` | integer | قیمت اصلی (تومان) |
| `off` | integer | درصد تخفیف (0 = بدون تخفیف) |
| `final_price` | integer | قیمت نهایی پس از تخفیف |
| `star` | float | امتیاز (0 تا 5) |

---

### 11. پرفروش‌ترین‌ها
```
GET /api/v1/products/best-sellers/
```

**Response `200`:** (همان ساختار محصولات ویژه)
```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "image": null,
      "name": "جاروبرقی رباتیک",
      "model": "RV-500",
      "star": 4.8,
      "price": 5500000,
      "off": 0,
      "final_price": 5500000
    }
  ]
}
```

---

### 12. محبوب‌ترین‌ها
```
GET /api/v1/products/most-popular/
```

**Response `200`:** (همان ساختار محصولات ویژه)

---

### 13. مقالات بلاگ
```
GET /api/v1/blog/posts/
```

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "image": "http://127.0.0.1:8000/media/blog/img.jpg",
      "title": "راهنمای خرید صندلی اداری",
      "subtitle": "چطور صندلی مناسب انتخاب کنیم؟",
      "date": "۱۵ خرداد ۱۴۰۵",
      "link": "/blog/1"
    }
  ]
}
```

> فیلد `date` به فرمت **تاریخ شمسی فارسی** است.

---

### 14. فوتر
```
GET /api/v1/footer/data/
```

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "social_links": [
      {
        "name": "instagram",
        "icon": "instagram-icon",
        "label": "اینستاگرام",
        "href": "https://instagram.com/..."
      }
    ],
    "customer_services": [
      { "text": "راهنمای خرید", "href": "/guide" }
    ],
    "products_links": [
      { "text": "محصولات جدید", "href": "/new" }
    ],
    "about_us_links": [
      { "text": "درباره ما", "href": "/about" }
    ],
    "feature_boxes": [
      {
        "icon": "truck",
        "title": "ارسال رایگان",
        "description": "برای خریدهای بالای ۵۰۰ هزار تومان"
      }
    ],
    "partner_logos": [
      {
        "src": "http://127.0.0.1:8000/media/partners/logo.jpg",
        "alt": "نام برند"
      }
    ]
  }
}
```

---

## صفحه محصول (Product Page)

---

### 15. جزئیات کامل محصول
```
GET /api/v1/products/{id}/
```

**Auth:** اختیاری — با توکن، `isInWishlist` و `isNotifyRequested` واقعی می‌شود.

**Response `200`:**
```json
{
  "data": {
    "id": 1,
    "name": "صندلی کارمندی کرکره‌ای",
    "model": "OC-200",
    "brand": "رایان",
    "star": 4.5,
    "reviewCount": 28,
    "inStock": true,
    "selectedColor": "مشکی",
    "images": [
      "http://127.0.0.1:8000/media/products/img1.jpg",
      "http://127.0.0.1:8000/media/products/img2.jpg"
    ],
    "price": 7000000,
    "off": 10,
    "colors": [
      { "name": "مشکی", "hex": "#000000" },
      { "name": "سفید", "hex": "#FFFFFF" }
    ],
    "warranties": [
      "۱۸ ماه گارانتی شرکتی",
      "۶ ماه ضمانت برگشت کالا"
    ],
    "features": [
      { "name": "جنس رویه", "value": "چرم مصنوعی" },
      { "name": "حداکثر وزن تحمل", "value": "۱۲۰ کیلوگرم" }
    ],
    "intro": [
      "این صندلی برای استفاده طولانی مدت طراحی شده است.",
      "با پشتی ارگونومیک و دسته قابل تنظیم."
    ],
    "specs": [
      { "name": "ابعاد", "value": "۶۰×۶۵×۱۱۵ سانتی‌متر" },
      { "name": "وزن", "value": "۱۵ کیلوگرم" }
    ],
    "review": {
      "text": "یک صندلی بسیار مناسب برای محیط اداری...",
      "pros": ["راحتی بالا", "طراحی زیبا", "دوام مناسب"],
      "cons": ["قیمت نسبتاً بالا", "مونتاژ زمان‌بر"]
    },
    "isInWishlist": false,
    "isNotifyRequested": false
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `reviewCount` | integer | تعداد کل نظرات |
| `inStock` | boolean | موجودی انبار |
| `selectedColor` | string \| null | نام رنگ پیش‌فرض |
| `images` | array of string | لیست تصاویر محصول |
| `off` | integer | درصد تخفیف |
| `colors` | array | رنگ‌های موجود |
| `warranties` | array of string | متون گارانتی |
| `features` | array | ویژگی‌ها (name, value) |
| `intro` | array of string | پاراگراف‌های معرفی |
| `specs` | array | مشخصات فنی (name, value) |
| `review` | object \| null | نقد سردبیری (ممکن است null باشد) |
| `isInWishlist` | boolean | در علاقه‌مندی‌ها است؟ (false اگر لاگین نباشد) |
| `isNotifyRequested` | boolean | اعلان موجودی فعال است؟ |

**خطا `404`:**
```json
{
  "error": { "code": 404, "message": "محصول یافت نشد" }
}
```

---

### 16. محصولات مشابه
```
GET /api/v1/products/{id}/similar/?limit={n}
```

**Query Params:**
| پارامتر | نوع | پیش‌فرض | توضیح |
|---------|-----|---------|-------|
| `limit` | integer | 10 | حداکثر تعداد محصول |

**Response `200`:**
```json
{
  "data": [
    {
      "id": 3,
      "name": "صندلی مدیریتی",
      "model": "MC-100",
      "image": "http://127.0.0.1:8000/media/products/img.jpg",
      "star": 4.2,
      "price": 9000000,
      "off": 0,
      "colors": [
        { "hex": "#000000" },
        { "hex": "#8B4513" }
      ]
    }
  ]
}
```

> محصولات هم‌دسته هستند و خود محصول جاری حذف شده است.

**خطا `404`:**
```json
{
  "error": { "code": 404, "message": "محصول یافت نشد" }
}
```

---

### 17. مقایسه محصولات
```
GET /api/v1/products/compare/?ids={id1},{id2},...
```

**Query Params:**
| پارامتر | نوع | اجباری | توضیح |
|---------|-----|--------|-------|
| `ids` | string | بله | آی‌دی‌ها با کاما — حداقل ۲ عدد |

**مثال:**
```
GET /api/v1/products/compare/?ids=1,3,5
```

**Response `200`:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "صندلی کارمندی کرکره‌ای",
      "model": "OC-200",
      "image": "http://127.0.0.1:8000/media/products/img.jpg",
      "price": 7000000,
      "off": 10,
      "star": 4.5,
      "specs": [
        { "name": "ابعاد", "value": "۶۰×۶۵×۱۱۵ سانتی‌متر" },
        { "name": "وزن", "value": "۱۵ کیلوگرم" }
      ]
    },
    {
      "id": 3,
      "name": "جاروبرقی رباتیک",
      "model": "RV-500",
      "image": null,
      "price": 5500000,
      "off": 0,
      "star": 0.0,
      "specs": []
    }
  ]
}
```

**خطاها:**
```json
// ids ارسال نشده
{ "error": { "code": 400, "message": "پارامتر ids الزامی است", "field": "ids" } }

// فقط یک آی‌دی
{ "error": { "code": 400, "message": "حداقل ۲ محصول برای مقایسه لازم است", "field": "ids" } }

// فرمت اشتباه (حروف به جای عدد)
{ "error": { "code": 400, "message": "فرمت ids نامعتبر است", "field": "ids" } }
```

---

### 18. لیست نظرات محصول
```
GET /api/v1/products/{id}/comments/
```

**Auth:** اختیاری — با توکن، فیلد `userVote` واقعی می‌شود.

**Query Params:**
| پارامتر | نوع | پیش‌فرض | توضیح |
|---------|-----|---------|-------|
| `page` | integer | 1 | شماره صفحه |
| `page_size` | integer | 10 | تعداد در هر صفحه (max: 50) |
| `star` | integer | — | فیلتر بر اساس امتیاز (1 تا 5) |

**Response `200`:**
```json
{
  "data": {
    "count": 28,
    "next": "http://127.0.0.1:8000/api/v1/products/1/comments/?page=2",
    "previous": null,
    "results": [
      {
        "id": 5,
        "user": "علی محمدی",
        "star": 5,
        "text": "کیفیت عالی، راحتی بسیار خوب",
        "date": "۱۵ خرداد ۱۴۰۵",
        "images": [
          { "image": "http://127.0.0.1:8000/media/comments/img.jpg" }
        ],
        "likes": 12,
        "dislikes": 1,
        "userVote": "like"
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `count` | integer | تعداد کل نظرات |
| `next` | string \| null | لینک صفحه بعد |
| `previous` | string \| null | لینک صفحه قبل |
| `userVote` | string \| null | `"like"` / `"dislike"` / `null` |

---

### 19. ثبت نظر جدید
```
POST /api/v1/products/{id}/comments/
```

**Auth:** اجباری

**Request Body:**
```json
{
  "star": 4,
  "text": "محصول خوبی بود، کیفیت ساخت مناسب"
}
```

| فیلد | نوع | اجباری | توضیح |
|------|-----|--------|-------|
| `star` | integer | بله | امتیاز ۱ تا ۵ |
| `text` | string | بله | متن نظر |

**Response `201`:**
```json
{
  "data": {
    "id": 12,
    "user": "رضا احمدی",
    "star": 4,
    "text": "محصول خوبی بود، کیفیت ساخت مناسب",
    "date": "۲۹ خرداد ۱۴۰۵",
    "images": [],
    "likes": 0,
    "dislikes": 0,
    "userVote": null
  },
  "message": "نظر شما با موفقیت ثبت شد"
}
```

**خطاها:**
```json
// بدون توکن
{ "error": { "code": 401, "message": "Authentication credentials were not provided." } }

// فیلد text خالی
{ "error": { "code": 400, "message": "This field may not be blank.", "field": "text" } }

// محصول وجود ندارد
{ "error": { "code": 404, "message": "محصول یافت نشد" } }
```

---

### 20. لایک / دیسلایک نظر
```
POST /api/v1/comments/{id}/helpful/
```

**Auth:** اجباری

> `{id}` آی‌دی **نظر** است.

**Request Body:**
```json
{
  "vote": "like"
}
```

| فیلد | مقادیر مجاز |
|------|------------|
| `vote` | `"like"` یا `"dislike"` |

**رفتار toggle:** اگر کاربر قبلاً همین رای را داده بود، رای حذف می‌شود.

**Response `200` — رای ثبت شد:**
```json
{
  "data": { "voted": true, "vote": "like" }
}
```

**Response `200` — رای قبلی حذف شد:**
```json
{
  "data": { "voted": false, "vote": null },
  "message": "رای حذف شد"
}
```

**خطاها:**
```json
// vote نامعتبر
{ "error": { "code": 400, "message": "مقدار vote باید like یا dislike باشد", "field": "vote" } }

// نظر وجود ندارد
{ "error": { "code": 404, "message": "نظر یافت نشد" } }
```

---

### 21. لیست سوالات محصول
```
GET /api/v1/products/{id}/questions/
```

**Auth:** اختیاری — با توکن، `userVote` پاسخ‌ها واقعی می‌شود.

**Query Params:**
| پارامتر | نوع | پیش‌فرض | توضیح |
|---------|-----|---------|-------|
| `page` | integer | 1 | شماره صفحه |
| `page_size` | integer | 10 | تعداد در هر صفحه (max: 50) |

**Response `200`:**
```json
{
  "data": {
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 3,
        "user": "مریم کریمی",
        "text": "آیا این صندلی تنظیم ارتفاع دارد؟",
        "date": "۱۰ خرداد ۱۴۰۵",
        "answers": [
          {
            "id": 7,
            "user": "پشتیبانی فروشگاه",
            "text": "بله، ارتفاع صندلی بین ۴۵ تا ۵۵ سانتی‌متر قابل تنظیم است.",
            "date": "۱۱ خرداد ۱۴۰۵",
            "likes": 8,
            "dislikes": 0,
            "userVote": null
          }
        ]
      }
    ]
  }
}
```

---

### 22. ثبت سوال جدید
```
POST /api/v1/products/{id}/questions/
```

**Auth:** اجباری

**Request Body:**
```json
{
  "text": "آیا این محصول گارانتی دارد؟"
}
```

**Response `201`:**
```json
{
  "data": {
    "id": 10,
    "user": "حسین نوری",
    "text": "آیا این محصول گارانتی دارد؟",
    "date": "۲۹ خرداد ۱۴۰۵",
    "answers": []
  },
  "message": "سوال شما با موفقیت ثبت شد"
}
```

---

### 23. ثبت پاسخ به سوال
```
POST /api/v1/questions/{id}/answers/
```

**Auth:** اجباری

> `{id}` آی‌دی **سوال** است، نه محصول.

**Request Body:**
```json
{
  "text": "بله، ۱۸ ماه گارانتی شرکتی دارد."
}
```

**Response `201`:**
```json
{
  "data": {
    "id": 15,
    "user": "پشتیبانی فروشگاه",
    "text": "بله، ۱۸ ماه گارانتی شرکتی دارد.",
    "date": "۲۹ خرداد ۱۴۰۵",
    "likes": 0,
    "dislikes": 0,
    "userVote": null
  },
  "message": "پاسخ شما با موفقیت ثبت شد"
}
```

**خطا `404`:**
```json
{ "error": { "code": 404, "message": "سوال یافت نشد" } }
```

---

### 24. لایک / دیسلایک پاسخ
```
POST /api/v1/answers/{id}/helpful/
```

**Auth:** اجباری

> `{id}` آی‌دی **پاسخ** است.

**Request Body:**
```json
{
  "vote": "dislike"
}
```

**رفتار toggle:** مشابه لایک نظر.

**Response `200` — رای ثبت:**
```json
{
  "data": { "voted": true, "vote": "dislike" }
}
```

**Response `200` — رای حذف (toggle):**
```json
{
  "data": { "voted": false, "vote": null },
  "message": "رای حذف شد"
}
```

---

### 25. افزودن / حذف از علاقه‌مندی‌ها
```
POST /api/v1/products/{id}/wishlist/
```

**Auth:** اجباری

**Request Body:** خالی (ارسال نکنید)

**رفتار toggle:** اگر محصول در wishlist بود حذف، اگر نبود اضافه می‌شود.

**Response `200` — اضافه شد:**
```json
{
  "data": { "isInWishlist": true },
  "message": "به علاقه‌مندی‌ها اضافه شد"
}
```

**Response `200` — حذف شد:**
```json
{
  "data": { "isInWishlist": false },
  "message": "از علاقه‌مندی‌ها حذف شد"
}
```

**خطاها:**
```json
// بدون توکن
{ "error": { "code": 401, "message": "Authentication credentials were not provided." } }

// محصول وجود ندارد
{ "error": { "code": 404, "message": "محصول یافت نشد" } }
```

---

### 26. اعلان موجودی شدن محصول
```
POST /api/v1/products/{id}/notify/
```

**Auth:** اجباری

**Request Body:** خالی (ارسال نکنید)

> این endpoint فقط برای محصولاتی کار می‌کند که `inStock: false` هستند.

**رفتار toggle:** اگر اعلان فعال بود غیرفعال می‌شود.

**Response `200` — اعلان فعال شد:**
```json
{
  "data": { "isNotifyRequested": true },
  "message": "اعلان موجودی فعال شد"
}
```

**Response `200` — اعلان لغو شد:**
```json
{
  "data": { "isNotifyRequested": false },
  "message": "اعلان موجودی لغو شد"
}
```

**خطاها:**
```json
// محصول موجود در انبار است
{ "error": { "code": 400, "message": "محصول در انبار موجود است", "field": "product_id" } }

// بدون توکن
{ "error": { "code": 401, "message": "Authentication credentials were not provided." } }

// محصول وجود ندارد
{ "error": { "code": 404, "message": "محصول یافت نشد" } }
```

---

## جدول کلی Endpoint ها

| # | Method | URL | Auth | توضیح |
|---|--------|-----|:----:|-------|
| 1 | `POST` | `/api/token/` | — | دریافت توکن |
| 2 | `POST` | `/api/token/refresh/` | — | تمدید توکن |
| **صفحه اصلی** | | | | |
| 3 | `GET` | `/api/v1/slider/` | — | اسلایدر |
| 4 | `GET` | `/api/v1/header/mega-menu/` | — | مگا منو |
| 5 | `GET` | `/api/v1/search/trending/` | — | جستجوهای پرتکرار |
| 6 | `GET` | `/api/v1/search/autocomplete/?q=` | — | پیشنهاد جستجو |
| 7 | `GET` | `/api/v1/banners/discount-main/` | — | بنر تخفیف اصلی |
| 8 | `GET` | `/api/v1/banners/single/` | — | بنر تکی |
| 9 | `GET` | `/api/v1/banners/double/` | — | بنر دوتایی |
| 10 | `GET` | `/api/v1/banners/footer-main/` | — | بنر فوتر |
| 11 | `GET` | `/api/v1/categories/main/` | — | دسته‌بندی‌های اصلی |
| 12 | `GET` | `/api/v1/products/featured/` | — | محصولات ویژه |
| 13 | `GET` | `/api/v1/products/best-sellers/` | — | پرفروش‌ترین‌ها |
| 14 | `GET` | `/api/v1/products/most-popular/` | — | محبوب‌ترین‌ها |
| 15 | `GET` | `/api/v1/blog/posts/` | — | مقالات بلاگ |
| 16 | `GET` | `/api/v1/footer/data/` | — | داده‌های فوتر |
| **صفحه محصول** | | | | |
| 17 | `GET` | `/api/v1/products/{id}/` | اختیاری | جزئیات کامل محصول |
| 18 | `GET` | `/api/v1/products/{id}/similar/?limit=` | — | محصولات مشابه |
| 19 | `GET` | `/api/v1/products/compare/?ids=` | — | مقایسه محصولات |
| 20 | `GET` | `/api/v1/products/{id}/comments/` | اختیاری | لیست نظرات |
| 21 | `POST` | `/api/v1/products/{id}/comments/` | ✓ | ثبت نظر |
| 22 | `POST` | `/api/v1/comments/{id}/helpful/` | ✓ | لایک/دیسلایک نظر |
| 23 | `GET` | `/api/v1/products/{id}/questions/` | اختیاری | لیست سوالات |
| 24 | `POST` | `/api/v1/products/{id}/questions/` | ✓ | ثبت سوال |
| 25 | `POST` | `/api/v1/questions/{id}/answers/` | ✓ | ثبت پاسخ |
| 26 | `POST` | `/api/v1/answers/{id}/helpful/` | ✓ | لایک/دیسلایک پاسخ |
| 27 | `POST` | `/api/v1/products/{id}/wishlist/` | ✓ | toggle علاقه‌مندی |
| 28 | `POST` | `/api/v1/products/{id}/notify/` | ✓ | toggle اعلان موجودی |

---

## نکات مهم برای فرانت

### مدیریت توکن
- `access token` رو در localStorage یا httpOnly cookie ذخیره کنید
- هر ۶۰ دقیقه با `refresh token` تمدید کنید
- اگر response `error.code === 401` بود، کاربر رو به صفحه لاگین ببرید

### تصاویر
- همه URL های تصویر **آدرس کامل** دارند — مستقیم در `<img src>` استفاده کنید
- مقدار `null` ممکن است — همیشه fallback تصویر placeholder داشته باشید

### قیمت‌ها
- همه قیمت‌ها **تومان** و integer هستند
- قیمت نهایی نمایشی: `price × (100 - off) / 100`
- اگر `off === 0` یعنی تخفیف ندارد

### Wishlist و Notify — toggle
- هر دو یک `POST` ساده هستند، body نمی‌خواهند
- وضعیت فعلی رو از `isInWishlist` / `isNotifyRequested` در جزئیات محصول بخوانید
- بعد از هر toggle، مقدار جدید در `data` برمی‌گردد — state محلی رو از آن آپدیت کنید

### Pagination
- `count` = تعداد کل آیتم‌ها
- `next` و `previous` آدرس کامل هستند یا `null`
- برای صفحه بعد فقط کافیه `next` رو fetch کنید

### رای‌دهی — toggle
- اگر کاربر دوباره همان رای رو بده، رای **حذف** می‌شود
- مقدار `voted: false` در response یعنی رای حذف شد

### تاریخ‌ها
- فیلدهای `date` در نظرات، سوالات و پاسخ‌ها به فرمت **شمسی فارسی** هستند: `"۱۵ خرداد ۱۴۰۵"`
- فیلد `expires_at` در بنرها به فرمت **ISO** است: `"2026-07-01"`

### دسته‌بندی در صفحه محصول — review
- فیلد `review` (نقد سردبیری) ممکن است `null` باشد
- `review.pros` و `review.cons` هر دو array of string هستند
