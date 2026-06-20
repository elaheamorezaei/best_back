# Admin Panel API Documentation

مستندات کامل API پنل مدیریت — برای پیاده‌سازی بک‌اند

---

## اطلاعات پایه

| پارامتر | مقدار |
|---|---|
| Base URL | `http://localhost:8000/api/v1` |
| Content-Type | `application/json` (یا `multipart/form-data` برای آپلود فایل) |
| Auth Header | `Authorization: Bearer <access_token>` |
| پیشوند همه endpointهای ادمین | `/admin/` |

### فرمت پاسخ خطا (یکنواخت برای همه endpointها)

```json
{
  "error": {
    "message": "پیام خطا به فارسی",
    "code": "ERROR_CODE",
    "errors": {
      "fieldName": "پیام خطای این فیلد"
    }
  }
}
```

### پاسخ Paginated (برای لیست‌ها)

```json
{
  "results": [ ...آرایه آیتم‌ها... ],
  "count": 150,
  "next": "http://localhost:8000/api/v1/admin/products/?page=3",
  "previous": "http://localhost:8000/api/v1/admin/products/?page=1"
}
```

### Query Params مشترک برای لیست‌ها

| پارامتر | نوع | توضیح |
|---|---|---|
| `page` | integer | شماره صفحه (پیش‌فرض: 1) |
| `pageSize` | integer | تعداد در هر صفحه (پیش‌فرض: 20) |
| `search` | string | جستجوی متنی |
| `ordering` | string | مرتب‌سازی (مثال: `-createdAt`, `name`) |

---

## ۱. احراز هویت ادمین

### `POST /admin/auth/login/`

ورود ادمین و دریافت توکن

**Request Body (JSON):**
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

**Response `200`:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "superadmin",
    "fullName": "مدیر سیستم",
    "avatar": "https://...",
    "isActive": true,
    "lastLogin": "2024-07-15T10:30:00Z",
    "createdAt": "2024-01-01T00:00:00Z"
  }
}
```

> **نکته:** `role` می‌تواند یکی از مقادیر `superadmin | admin | editor | support` باشد.

---

### `POST /admin/auth/refresh/`

تمدید توکن دسترسی

**Request Body (JSON):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response `200`:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### `POST /admin/auth/logout/`

خروج (باطل‌کردن refresh token)

**Request Body (JSON):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response `204 No Content`**

---

## ۲. داشبورد

### `GET /admin/dashboard/stats/`

آمار کلی برای کارت‌های داشبورد

**Response `200`:**
```json
{
  "totalRevenue": 128500000,
  "revenueGrowth": 12.5,
  "totalOrders": 1240,
  "ordersGrowth": 8.3,
  "totalProducts": 86,
  "productsGrowth": 4.1,
  "totalUsers": 3420,
  "usersGrowth": 15.7,
  "pendingOrders": 12,
  "lowStockProducts": 5,
  "newMessages": 8,
  "pendingReviews": 14
}
```

> `revenueGrowth` درصد رشد نسبت به دوره قبل است (می‌تواند منفی باشد).

---

### `GET /admin/dashboard/revenue/?period=month`

داده نمودار درآمد

**Query Params:**

| پارامتر | مقادیر | پیش‌فرض |
|---|---|---|
| `period` | `week` \| `month` \| `year` | `month` |

**Response `200`:**
```json
[
  { "label": "فروردین", "revenue": 12400000, "orders": 145 },
  { "label": "اردیبهشت", "revenue": 15800000, "orders": 180 },
  { "label": "خرداد", "revenue": 11200000, "orders": 130 }
]
```

> برای `week`: برچسب روزهای هفته (شنبه، یکشنبه، ...)  
> برای `month`: برچسب ماه‌های شمسی  
> برای `year`: برچسب سال‌های اخیر

---

### `GET /admin/dashboard/top-products/`

پرفروش‌ترین محصولات (۵ آیتم)

**Response `200`:**
```json
[
  {
    "id": 1,
    "name": "مبل راحتی مدرن",
    "image": "https://cdn.example.com/products/1.jpg",
    "sales": 48,
    "revenue": 117600000
  }
]
```

---

### `GET /admin/dashboard/recent-orders/`

سفارش‌های اخیر (۵ آیتم)

**Response `200`:**
```json
[
  {
    "id": 123,
    "orderNumber": "ORD-1200",
    "customerName": "علی محمدی",
    "total": 4800000,
    "status": "processing",
    "createdAt": "2024-07-15T09:00:00Z"
  }
]
```

---

## ۳. محصولات

### `GET /admin/products/`

لیست محصولات (paginated)

**Query Params اضافه:**

| پارامتر | نوع | توضیح |
|---|---|---|
| `search` | string | جستجو در نام، SKU |
| `category` | integer | فیلتر بر اساس دسته‌بندی |
| `isActive` | boolean | فیلتر فعال/غیرفعال |
| `isFeatured` | boolean | فیلتر محصول ویژه |
| `lowStock` | boolean | فقط محصولات کم‌موجودی |

**Response `200`:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "مبل راحتی مدرن",
      "slug": "modern-comfort-sofa",
      "sku": "SKU-1001",
      "description": "<p>توضیحات کامل...</p>",
      "shortDescription": "مبل راحتی با طراحی مدرن",
      "price": 2450000,
      "comparePrice": 2900000,
      "costPrice": 1800000,
      "stock": 15,
      "minStock": 5,
      "weight": 45.0,
      "categoryId": 1,
      "categoryName": "مبلمان",
      "tags": ["مبل", "راحتی", "مدرن"],
      "images": [
        {
          "id": 1,
          "url": "https://cdn.example.com/products/1-main.jpg",
          "alt": "مبل راحتی مدرن",
          "isPrimary": true,
          "order": 1
        },
        {
          "id": 2,
          "url": "https://cdn.example.com/products/1-side.jpg",
          "alt": "مبل از زاویه دید",
          "isPrimary": false,
          "order": 2
        }
      ],
      "variants": [
        { "id": 1, "name": "رنگ", "value": "کرم", "stock": 8 },
        { "id": 2, "name": "رنگ", "value": "خاکستری", "price": 2600000, "stock": 7 }
      ],
      "attributes": [
        { "id": 1, "name": "جنس پارچه", "value": "میکروفایبر" },
        { "id": 2, "name": "ابعاد", "value": "220×90", "unit": "cm" }
      ],
      "isActive": true,
      "isFeatured": true,
      "isNew": false,
      "isSale": false,
      "rating": 4.2,
      "reviewCount": 23,
      "salesCount": 48,
      "seo": {
        "metaTitle": "مبل راحتی مدرن | فروشگاه",
        "metaDescription": "خرید مبل راحتی مدرن...",
        "keywords": ["مبل راحتی", "مبل مدرن"],
        "ogImage": "https://cdn.example.com/og/1.jpg",
        "noIndex": false,
        "noFollow": false
      },
      "createdAt": "2024-01-15T10:00:00Z",
      "updatedAt": "2024-07-15T10:00:00Z"
    }
  ],
  "count": 86,
  "next": null,
  "previous": null
}
```

---

### `POST /admin/products/`

ایجاد محصول جدید

**Request Body (`multipart/form-data`):**

| فیلد | نوع | اجباری | توضیح |
|---|---|---|---|
| `name` | string | ✅ | نام محصول |
| `slug` | string | ✅ | اسلاگ یکتا (حروف انگلیسی و خط تیره) |
| `sku` | string | ✅ | کد محصول یکتا |
| `description` | string | ✅ | توضیحات کامل (HTML) |
| `shortDescription` | string | — | توضیحات کوتاه |
| `price` | number | ✅ | قیمت فروش (تومان) |
| `comparePrice` | number | — | قیمت قبل از تخفیف |
| `costPrice` | number | — | قیمت تمام‌شده |
| `stock` | integer | ✅ | موجودی انبار |
| `minStock` | integer | — | حداقل موجودی (پیش‌فرض: 0) |
| `weight` | number | — | وزن (کیلوگرم) |
| `categoryId` | integer | ✅ | شناسه دسته‌بندی |
| `tags` | string (JSON array) | — | `["مبل","راحتی"]` |
| `images` | File[] | — | فایل‌های تصویر (ترتیب = اولویت) |
| `variants` | string (JSON array) | — | آرایه JSON تنوع‌ها |
| `attributes` | string (JSON array) | — | آرایه JSON ویژگی‌ها |
| `isActive` | boolean | — | پیش‌فرض: true |
| `isFeatured` | boolean | — | پیش‌فرض: false |
| `isNew` | boolean | — | پیش‌فرض: false |
| `isSale` | boolean | — | پیش‌فرض: false |
| `seo` | string (JSON) | — | شیء JSON اطلاعات SEO |

**variants JSON (نمونه):**
```json
[
  { "name": "رنگ", "value": "کرم", "stock": 8 },
  { "name": "رنگ", "value": "خاکستری", "price": 2600000, "stock": 7 }
]
```

**attributes JSON (نمونه):**
```json
[
  { "name": "جنس پارچه", "value": "میکروفایبر" },
  { "name": "ابعاد", "value": "220×90", "unit": "cm" }
]
```

**seo JSON (نمونه):**
```json
{
  "metaTitle": "مبل راحتی | فروشگاه",
  "metaDescription": "خرید...",
  "keywords": ["مبل", "راحتی"],
  "canonicalUrl": "https://example.com/product/modern-comfort-sofa",
  "ogTitle": "مبل راحتی مدرن",
  "ogDescription": "...",
  "ogImage": "https://cdn.example.com/og/1.jpg",
  "noIndex": false,
  "noFollow": false,
  "structuredData": "{\"@context\":\"https://schema.org\",...}"
}
```

**Response `201`:** شیء `AdminProduct` کامل (مثل GET)

---

### `GET /admin/products/{id}/`

دریافت یک محصول

**Response `200`:** شیء `AdminProduct` کامل

---

### `PATCH /admin/products/{id}/`

ویرایش محصول (`multipart/form-data` — فقط فیلدهای تغییریافته)

**Response `200`:** شیء `AdminProduct` بروز شده

---

### `DELETE /admin/products/{id}/`

حذف محصول

**Response `204 No Content`**

---

### `POST /admin/products/{id}/toggle-active/`

تغییر وضعیت فعال/غیرفعال

**Response `200`:**
```json
{ "isActive": false }
```

---

### `POST /admin/products/{id}/toggle-featured/`

تغییر وضعیت ویژه

**Response `200`:**
```json
{ "isFeatured": true }
```

---

### `POST /admin/products/bulk-delete/`

حذف دسته‌جمعی

**Request Body (JSON):**
```json
{ "ids": [1, 2, 3, 5] }
```

**Response `200`:**
```json
{ "deleted": 4 }
```

---

## ۴. دسته‌بندی‌ها

### `GET /admin/categories/`

لیست دسته‌بندی‌ها (paginated)

**Response `200`:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "مبلمان",
      "slug": "furniture",
      "description": "انواع مبلمان خانگی",
      "image": "https://cdn.example.com/cats/furniture.jpg",
      "parentId": null,
      "parentName": null,
      "order": 1,
      "isActive": true,
      "productCount": 32,
      "seo": { "metaTitle": "...", "metaDescription": "..." },
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "count": 8
}
```

---

### `GET /admin/categories/all/`

همه دسته‌بندی‌ها بدون pagination (برای dropdown)

**Response `200`:** آرایه‌ای از `AdminCategory` (بدون `results` wrapper)

---

### `POST /admin/categories/`

ایجاد دسته‌بندی (`multipart/form-data`)

| فیلد | نوع | اجباری |
|---|---|---|
| `name` | string | ✅ |
| `slug` | string | ✅ |
| `description` | string | — |
| `image` | File | — |
| `parentId` | integer | — |
| `order` | integer | — |
| `isActive` | boolean | — |
| `seo` | string (JSON) | — |

**Response `201`:** شیء `AdminCategory`

---

### `GET /admin/categories/{id}/`

دریافت یک دسته‌بندی → **Response `200`:** شیء `AdminCategory`

### `PATCH /admin/categories/{id}/`

ویرایش (`multipart/form-data`) → **Response `200`:** شیء `AdminCategory`

### `DELETE /admin/categories/{id}/`

**Response `204`** ⚠️ اگر دسته دارای زیرمجموعه یا محصول باشد، خطای `409 Conflict` برگردانده شود.

---

### `POST /admin/categories/reorder/`

تغییر ترتیب دسته‌بندی‌ها

**Request Body (JSON):**
```json
{
  "items": [
    { "id": 1, "order": 1 },
    { "id": 3, "order": 2 },
    { "id": 2, "order": 3 }
  ]
}
```

**Response `200`:** `{ "updated": 3 }`

---

## ۵. سفارش‌ها

### `GET /admin/orders/`

لیست سفارش‌ها (paginated)

**Query Params اضافه:**

| پارامتر | نوع | توضیح |
|---|---|---|
| `status` | string | فیلتر وضعیت سفارش |
| `paymentStatus` | string | `pending` \| `paid` \| `failed` \| `refunded` |
| `startDate` | string | از تاریخ (ISO 8601) |
| `endDate` | string | تا تاریخ (ISO 8601) |

**Response `200`:**
```json
{
  "results": [
    {
      "id": 123,
      "orderNumber": "ORD-1200",
      "status": "processing",
      "paymentStatus": "paid",
      "paymentMethod": "درگاه بانکی",
      "customer": {
        "id": 5,
        "name": "علی محمدی",
        "email": "ali@example.com",
        "phone": "09121234567"
      },
      "items": [
        {
          "id": 1,
          "productId": 1,
          "productName": "مبل راحتی مدرن",
          "productImage": "https://cdn.example.com/products/1.jpg",
          "variant": "رنگ: کرم",
          "price": 2450000,
          "quantity": 1,
          "total": 2450000
        }
      ],
      "shippingAddress": {
        "fullName": "علی محمدی",
        "phone": "09121234567",
        "province": "تهران",
        "city": "تهران",
        "address": "خیابان ولیعصر، پلاک ۱۲",
        "postalCode": "1234567890",
        "lat": 35.6892,
        "lng": 51.3890
      },
      "subtotal": 4850000,
      "shippingCost": 150000,
      "discount": 200000,
      "tax": 0,
      "total": 4800000,
      "discountCode": "SUMMER20",
      "notes": "لطفاً با دقت ارسال شود",
      "trackingCode": "1234567890",
      "createdAt": "2024-07-15T09:00:00Z",
      "updatedAt": "2024-07-15T12:00:00Z"
    }
  ],
  "count": 1240
}
```

---

### `GET /admin/orders/{id}/`

دریافت جزئیات یک سفارش → **Response `200`:** شیء `AdminOrder` کامل

---

### `PATCH /admin/orders/{id}/`

بروزرسانی وضعیت و کد رهگیری

**Request Body (JSON):**
```json
{
  "status": "shipped",
  "trackingCode": "9876543210"
}
```

> **وضعیت‌های مجاز:** `pending | processing | shipped | delivered | cancelled | refunded`

**Response `200`:** شیء `AdminOrder` بروز شده

---

### `POST /admin/orders/{id}/note/`

افزودن یادداشت به سفارش

**Request Body (JSON):**
```json
{ "note": "با انبار هماهنگ شد." }
```

**Response `200`:**
```json
{
  "id": 1,
  "author": "ادمین",
  "text": "با انبار هماهنگ شد.",
  "time": "2024-07-15T11:00:00Z",
  "isAdmin": true
}
```

---

### `POST /admin/orders/{id}/cancel/`

لغو سفارش

**Request Body (JSON):**
```json
{ "reason": "درخواست مشتری" }
```

**Response `200`:** شیء `AdminOrder` با `status: "cancelled"`

---

### `POST /admin/orders/{id}/refund/`

استرداد وجه

**Request Body (JSON):**
```json
{ "amount": 4800000 }
```

> اگر `amount` خالی باشد، مبلغ کامل سفارش استرداد می‌شود.

**Response `200`:** شیء `AdminOrder` با `paymentStatus: "refunded"`

---

## ۶. کاربران

### `GET /admin/users/`

لیست کاربران (paginated)

**Query Params اضافه:** `isActive`, `startDate`, `endDate`

**Response `200`:**
```json
{
  "results": [
    {
      "id": 5,
      "fullName": "علی محمدی",
      "email": "ali@example.com",
      "phone": "09121234567",
      "avatar": "https://cdn.example.com/avatars/5.jpg",
      "isActive": true,
      "ordersCount": 12,
      "totalSpent": 28400000,
      "walletBalance": 500000,
      "joinedAt": "2024-01-10T08:00:00Z",
      "lastLogin": "2024-07-14T18:30:00Z"
    }
  ],
  "count": 3420
}
```

---

### `GET /admin/users/{id}/`

دریافت یک کاربر → **Response `200`:** شیء `AdminUserItem`

---

### `POST /admin/users/{id}/toggle-active/`

فعال/غیرفعال‌کردن کاربر

**Response `200`:** `{ "isActive": false }`

---

### `POST /admin/users/{id}/wallet/`

افزایش یا کاهش موجودی کیف‌پول

**Request Body (JSON):**
```json
{
  "amount": 100000,
  "description": "جبران خسارت سفارش ORD-1200"
}
```

> `amount` مثبت = افزایش، `amount` منفی = کاهش

**Response `200`:**
```json
{
  "walletBalance": 600000,
  "transaction": {
    "id": 45,
    "amount": 100000,
    "description": "جبران خسارت سفارش ORD-1200",
    "createdAt": "2024-07-15T11:00:00Z"
  }
}
```

---

### `DELETE /admin/users/{id}/`

حذف کاربر → **Response `204`**

---

## ۷. بلاگ

### `GET /admin/blog/`

لیست مقالات (paginated)

**Query Params اضافه:** `isPublished`, `isFeatured`, `categoryId`

**Response `200`:**
```json
{
  "results": [
    {
      "id": 1,
      "title": "راهنمای انتخاب مبلمان",
      "slug": "furniture-selection-guide",
      "excerpt": "انتخاب مبلمان مناسب...",
      "content": "<p>...</p>",
      "coverImage": "https://cdn.example.com/blog/1.jpg",
      "categoryId": 1,
      "categoryName": "مبلمان",
      "tags": ["مبلمان", "دکوراسیون"],
      "isPublished": true,
      "isFeatured": false,
      "viewCount": 2450,
      "commentCount": 18,
      "seo": { "metaTitle": "...", "metaDescription": "..." },
      "publishedAt": "2024-06-01T08:00:00Z",
      "createdAt": "2024-05-28T10:00:00Z",
      "updatedAt": "2024-07-10T10:00:00Z"
    }
  ],
  "count": 24
}
```

---

### `POST /admin/blog/`

ایجاد مقاله (`multipart/form-data`)

| فیلد | نوع | اجباری |
|---|---|---|
| `title` | string | ✅ |
| `slug` | string | ✅ |
| `excerpt` | string | — |
| `content` | string (HTML) | ✅ |
| `coverImage` | File | — |
| `categoryId` | integer | — |
| `tags` | string (JSON array) | — |
| `isPublished` | boolean | — |
| `isFeatured` | boolean | — |
| `seo` | string (JSON) | — |

**Response `201`:** شیء `AdminBlogPost`

---

### `GET /admin/blog/{id}/`

→ **Response `200`:** شیء `AdminBlogPost`

### `PATCH /admin/blog/{id}/`

→ **Response `200`:** شیء `AdminBlogPost` بروز شده

### `DELETE /admin/blog/{id}/`

→ **Response `204`**

---

### `POST /admin/blog/{id}/toggle-publish/`

انتشار/پیش‌نویس مقاله

**Response `200`:**
```json
{
  "isPublished": true,
  "publishedAt": "2024-07-15T12:00:00Z"
}
```

---

## ۸. بنرها

### `GET /admin/banners/`

**Response `200` (آرایه مستقیم، بدون pagination):**
```json
[
  {
    "id": 1,
    "title": "تخفیف ویژه تابستان",
    "subtitle": "تا ۳۰٪ تخفیف روی مبلمان",
    "image": "https://cdn.example.com/banners/summer.jpg",
    "mobileImage": "https://cdn.example.com/banners/summer-mobile.jpg",
    "link": "/sale",
    "buttonText": "مشاهده محصولات",
    "position": "hero",
    "isActive": true,
    "order": 1,
    "startDate": "2024-06-21",
    "endDate": "2024-07-21"
  }
]
```

> **position:** `hero | sidebar | middle | bottom`

---

### `POST /admin/banners/` (`multipart/form-data`)

| فیلد | نوع | اجباری |
|---|---|---|
| `title` | string | ✅ |
| `subtitle` | string | — |
| `image` | File | ✅ |
| `mobileImage` | File | — |
| `link` | string | — |
| `buttonText` | string | — |
| `position` | string | ✅ |
| `isActive` | boolean | — |
| `order` | integer | — |
| `startDate` | string (ISO date) | — |
| `endDate` | string (ISO date) | — |

**Response `201`:** شیء `AdminBanner`

### `GET /admin/banners/{id}/` → `200` شیء `AdminBanner`
### `PATCH /admin/banners/{id}/` → `200` شیء `AdminBanner`
### `DELETE /admin/banners/{id}/` → `204`

---

### `POST /admin/banners/reorder/`

**Request Body (JSON):** `{ "items": [{ "id": 1, "order": 2 }, { "id": 2, "order": 1 }] }`  
**Response `200`:** `{ "updated": 2 }`

---

## ۹. اسلایدر

### `GET /admin/sliders/`

**Response `200` (آرایه مستقیم):**
```json
[
  {
    "id": 1,
    "title": "کلکسیون جدید پاییز",
    "subtitle": "طراحی مدرن برای خانه شما",
    "image": "https://cdn.example.com/sliders/1.jpg",
    "mobileImage": "https://cdn.example.com/sliders/1-mobile.jpg",
    "link": "/category/new",
    "buttonText": "خرید کنید",
    "isActive": true,
    "order": 1
  }
]
```

### `POST /admin/sliders/` (`multipart/form-data`)

| فیلد | نوع | اجباری |
|---|---|---|
| `title` | string | ✅ |
| `subtitle` | string | — |
| `image` | File | ✅ |
| `mobileImage` | File | — |
| `link` | string | — |
| `buttonText` | string | — |
| `isActive` | boolean | — |
| `order` | integer | — |

**Response `201`:** شیء `AdminSlider`

### `PATCH /admin/sliders/{id}/` → `200` شیء `AdminSlider`
### `DELETE /admin/sliders/{id}/` → `204`

### `POST /admin/sliders/reorder/`
**Request Body:** `{ "items": [{ "id": 1, "order": 1 }, ...] }`  
**Response `200`:** `{ "updated": N }`

---

## ۱۰. سوالات متداول (FAQ)

### دسته‌بندی FAQ

#### `GET /admin/faq/categories/`
**Response `200` (آرایه مستقیم):**
```json
[
  { "id": 1, "name": "پرداخت و خرید", "icon": "💳", "order": 1, "isActive": true },
  { "id": 2, "name": "ارسال و تحویل", "icon": "📦", "order": 2, "isActive": true }
]
```

#### `POST /admin/faq/categories/`
**Request Body (JSON):**
```json
{ "name": "گارانتی و بازگشت", "icon": "🛡️", "order": 3, "isActive": true }
```
**Response `201`:** شیء `AdminFAQCategory`

#### `PATCH /admin/faq/categories/{id}/` → `200` شیء `AdminFAQCategory`
#### `DELETE /admin/faq/categories/{id}/` → `204`

---

### سوالات FAQ

#### `GET /admin/faq/`

**Query Params اضافه:** `categoryId`, `isActive`

**Response `200` (paginated):**
```json
{
  "results": [
    {
      "id": 1,
      "question": "روش‌های پرداخت چیست؟",
      "answer": "می‌توانید از طریق درگاه بانکی...",
      "categoryId": 1,
      "categoryName": "پرداخت و خرید",
      "order": 1,
      "isActive": true,
      "viewCount": 540
    }
  ],
  "count": 28
}
```

#### `POST /admin/faq/`
**Request Body (JSON):**
```json
{
  "question": "آیا امکان مرجوعی وجود دارد؟",
  "answer": "بله، تا ۷ روز پس از تحویل...",
  "categoryId": 3,
  "order": 1,
  "isActive": true
}
```
**Response `201`:** شیء `AdminFAQ`

#### `PATCH /admin/faq/{id}/` → `200` شیء `AdminFAQ`
#### `DELETE /admin/faq/{id}/` → `204`

#### `POST /admin/faq/reorder/`
**Request Body:** `{ "items": [{ "id": 1, "order": 2 }, ...] }`  
**Response `200`:** `{ "updated": N }`

---

## ۱۱. کدهای تخفیف

### `GET /admin/discounts/`

**Query Params اضافه:** `isActive`, `type`

**Response `200` (paginated):**
```json
{
  "results": [
    {
      "id": 1,
      "code": "SUMMER20",
      "type": "percentage",
      "value": 20,
      "minOrderAmount": 500000,
      "maxDiscount": 200000,
      "usageLimit": 100,
      "usedCount": 45,
      "perUserLimit": 1,
      "isActive": true,
      "startDate": "2024-06-21",
      "endDate": "2024-09-22",
      "applicableProducts": [],
      "applicableCategories": [1, 3],
      "createdAt": "2024-06-18T10:00:00Z"
    }
  ],
  "count": 12
}
```

> **type:** `percentage` (درصدی) یا `fixed` (مبلغ ثابت به تومان)

---

### `POST /admin/discounts/`
**Request Body (JSON):**
```json
{
  "code": "NEWUSER",
  "type": "fixed",
  "value": 50000,
  "minOrderAmount": 300000,
  "maxDiscount": null,
  "usageLimit": 500,
  "perUserLimit": 1,
  "isActive": true,
  "startDate": "2024-07-01",
  "endDate": "2024-12-31",
  "applicableProducts": [],
  "applicableCategories": []
}
```
**Response `201`:** شیء `AdminDiscount`

### `GET /admin/discounts/{id}/` → `200`
### `PATCH /admin/discounts/{id}/` → `200`
### `DELETE /admin/discounts/{id}/` → `204`

### `POST /admin/discounts/{id}/toggle-active/`
**Response `200`:** `{ "isActive": false }`

---

## ۱۲. پیام‌های تماس

### `GET /admin/messages/`

**Query Params اضافه:** `isRead`, `isReplied`

**Response `200` (paginated):**
```json
{
  "results": [
    {
      "id": 1,
      "name": "رضا کریمی",
      "email": "reza@example.com",
      "phone": "09131234567",
      "subject": "سوال درباره ضمانت",
      "message": "سلام، می‌خواستم بدونم ضمانت محصولات چقدره؟",
      "isRead": false,
      "isReplied": false,
      "reply": null,
      "repliedAt": null,
      "createdAt": "2024-07-14T15:30:00Z"
    }
  ],
  "count": 8
}
```

---

### `GET /admin/messages/{id}/`
→ **Response `200`:** شیء `AdminMessage` (و به‌طور خودکار `isRead: true` شود)

### `POST /admin/messages/{id}/reply/`
**Request Body (JSON):**
```json
{ "reply": "سلام رضا عزیز، ضمانت محصولات ما ۲ سال است." }
```
**Response `200`:** شیء `AdminMessage` با فیلدهای `isReplied: true`, `reply`, `repliedAt`

### `POST /admin/messages/{id}/mark-read/`
**Response `200`:** `{ "isRead": true }`

### `DELETE /admin/messages/{id}/` → `204`

### `POST /admin/messages/bulk-delete/`
**Request Body (JSON):** `{ "ids": [1, 2, 5] }`  
**Response `200`:** `{ "deleted": 3 }`

---

## ۱۳. نظرات محصولات

### `GET /admin/reviews/`

**Query Params اضافه:** `isApproved`, `productId`, `rating`

**Response `200` (paginated):**
```json
{
  "results": [
    {
      "id": 1,
      "productId": 1,
      "productName": "مبل راحتی مدرن",
      "userId": 5,
      "userName": "علی محمدی",
      "rating": 5,
      "title": "عالی بود",
      "comment": "کیفیت بسیار بالاست و...",
      "pros": ["کیفیت عالی", "ارسال سریع"],
      "cons": ["قیمت بالاست"],
      "isApproved": false,
      "isVerified": true,
      "helpfulCount": 12,
      "createdAt": "2024-07-10T20:00:00Z"
    }
  ],
  "count": 14
}
```

> `isVerified: true` = کاربر این محصول را خریداری کرده است

---

### `POST /admin/reviews/{id}/approve/`
**Response `200`:** `{ "isApproved": true }`

### `POST /admin/reviews/{id}/reject/`
**Response `200`:** `{ "isApproved": false }`

### `DELETE /admin/reviews/{id}/` → `204`

### `POST /admin/reviews/bulk-approve/`
**Request Body:** `{ "ids": [1, 2, 4] }`  
**Response `200`:** `{ "approved": 3 }`

---

## ۱۴. تنظیمات

### `GET /admin/settings/site/`

**Response `200`:**
```json
{
  "siteName": "فروشگاه آنلاین",
  "siteDescription": "بهترین فروشگاه مبلمان",
  "siteKeywords": ["مبل", "دکوراسیون", "فروشگاه آنلاین"],
  "logo": "https://cdn.example.com/logo.png",
  "favicon": "https://cdn.example.com/favicon.ico",
  "email": "info@example.com",
  "phone": "021-12345678",
  "address": "تهران، خیابان ولیعصر",
  "instagram": "https://instagram.com/shop",
  "telegram": "https://t.me/shop",
  "whatsapp": "09121234567",
  "googleAnalyticsId": "G-XXXXXXXX",
  "googleTagManagerId": "GTM-XXXXXXX",
  "robotsTxt": "User-agent: *\nAllow: /",
  "maintenanceMode": false
}
```

---

### `PATCH /admin/settings/site/` (`multipart/form-data`)

| فیلد | نوع | توضیح |
|---|---|---|
| `siteName` | string | — |
| `siteDescription` | string | — |
| `siteKeywords` | string (JSON array) | — |
| `logo` | File | — |
| `favicon` | File | — |
| `email` | string | — |
| `phone` | string | — |
| `address` | string | — |
| `instagram` | string | — |
| `telegram` | string | — |
| `whatsapp` | string | — |
| `googleAnalyticsId` | string | — |
| `googleTagManagerId` | string | — |
| `robotsTxt` | string | — |
| `maintenanceMode` | boolean | — |

**Response `200`:** شیء `SiteSettings`

---

### `GET /admin/settings/theme/`

**Response `200`:**
```json
{
  "primary": "#ef4444",
  "secondary": "#f59e0b",
  "accent": "#8b5cf6",
  "neutral": "#6b7280",
  "base": "#ffffff",
  "info": "#3b82f6",
  "success": "#22c55e",
  "warning": "#f59e0b",
  "error": "#ef4444",
  "radius": "0.75rem",
  "fontFamily": "Vazir",
  "mode": "light"
}
```

---

### `PUT /admin/settings/theme/`

**Request Body (JSON):** همان ساختار بالا (کل شیء جایگزین می‌شود)

**Response `200`:** شیء `ThemeSettings`

---

### `GET /admin/settings/seo/`

تنظیمات SEO همه صفحات

**Response `200` (آرایه مستقیم):**
```json
[
  {
    "page": "صفحه اصلی",
    "path": "/",
    "metaTitle": "فروشگاه آنلاین | بهترین مبلمان",
    "metaDescription": "خرید انواع مبلمان با قیمت مناسب...",
    "keywords": ["مبل", "فروشگاه آنلاین"],
    "ogImage": "https://cdn.example.com/og/home.jpg",
    "noIndex": false
  },
  {
    "page": "لیست محصولات",
    "path": "/products",
    "metaTitle": "همه محصولات | فروشگاه",
    "metaDescription": "...",
    "keywords": [],
    "ogImage": null,
    "noIndex": false
  }
]
```

---

### `POST /admin/settings/seo/`

ذخیره/بروزرسانی SEO یک صفحه (upsert بر اساس `path`)

**Request Body (JSON):**
```json
{
  "page": "صفحه اصلی",
  "path": "/",
  "metaTitle": "فروشگاه آنلاین | بهترین مبلمان",
  "metaDescription": "خرید انواع مبلمان...",
  "keywords": ["مبل", "فروشگاه"],
  "ogImage": "https://cdn.example.com/og/home.jpg",
  "noIndex": false
}
```

**Response `200`:** شیء `SEOPageSettings`

---

## ۱۵. گزارش‌ها

### `POST /admin/reports/sales/`

گزارش فروش

**Request Body (JSON):**
```json
{
  "startDate": "2024-04-01",
  "endDate": "2024-06-30",
  "groupBy": "month",
  "category": null,
  "status": "delivered"
}
```

> `groupBy`: `day | week | month`

**Response `200`:**
```json
[
  {
    "period": "فروردین ۱۴۰۳",
    "orders": 145,
    "revenue": 12400000,
    "averageOrderValue": 855172,
    "newCustomers": 38
  },
  {
    "period": "اردیبهشت ۱۴۰۳",
    "orders": 180,
    "revenue": 15800000,
    "averageOrderValue": 877778,
    "newCustomers": 52
  }
]
```

---

### `POST /admin/reports/products/`

گزارش محصولات

**Request Body (JSON):** همان `ReportFilter`

**Response `200`:**
```json
[
  {
    "productId": 1,
    "productName": "مبل راحتی مدرن",
    "category": "مبلمان",
    "unitsSold": 48,
    "revenue": 117600000,
    "returns": 2,
    "currentStock": 15
  }
]
```

---

### `POST /admin/reports/orders/`

فیلتر سفارش‌ها برای گزارش

**Request Body (JSON):** همان `ReportFilter`

**Response `200`:** آرایه `AdminOrder`

---

## ۱۶. آپلود فایل (عمومی)

### `POST /admin/upload/`

آپلود تصویر و دریافت URL

**Request Body (`multipart/form-data`):**

| فیلد | نوع | توضیح |
|---|---|---|
| `file` | File | فایل تصویر (JPG, PNG, WebP — حداکثر ۵MB) |
| `folder` | string | پوشه هدف: `products | blog | banners | sliders | settings` |

**Response `200`:**
```json
{
  "url": "https://cdn.example.com/products/uuid-filename.jpg",
  "width": 1200,
  "height": 800,
  "size": 245600
}
```

---

## نکات پیاده‌سازی

### احراز هویت

- همه endpointهای `/admin/` نیاز به `Authorization: Bearer <access_token>` دارند
- Token باید JWT باشد با فیلد `role` در payload
- Access token: TTL پیشنهادی ۱۵ دقیقه
- Refresh token: TTL پیشنهادی ۷ روز

### مدیریت فایل

- فایل‌ها را در CDN ذخیره کنید و URL کامل برگردانید
- برای `multipart/form-data`: فیلدهای JSON (مثل `tags`, `variants`, `seo`) به صورت **string serialized** ارسال می‌شوند
  - بک‌اند باید آن‌ها را با `json.loads()` parse کند

### فرمت تاریخ

- همه تاریخ‌ها در Response به فرمت **ISO 8601** باشند (`2024-07-15T10:30:00Z`)
- تاریخ‌های فارسی (نمایشی) در فرانت‌اند تبدیل می‌شوند

### Soft Delete

- محصولات، کاربران و بلاگ‌ها را soft delete کنید (فیلد `isDeleted`)
- در لیست‌ها فیلتر `isDeleted=false` اعمال شود

### کدهای HTTP

| کد | معنا |
|---|---|
| `200` | موفق |
| `201` | ایجاد شد |
| `204` | حذف شد (بدون محتوا) |
| `400` | خطای اعتبارسنجی |
| `401` | احراز هویت نشده |
| `403` | دسترسی ندارید |
| `404` | یافت نشد |
| `409` | تعارض (مثلاً slug تکراری) |
| `500` | خطای سرور |
