# Admin API Reference

Base URL: `/api/v1/`

All endpoints (except Auth) require the header:
```
Authorization: Bearer <access_token>
```

The user must have `is_staff = true` on Django's User model.

---

## Error Format

All errors follow this shape:
```json
{
  "error": {
    "message": "پیام خطا",
    "code": "ERROR_CODE"
  }
}
```

Common HTTP status codes:
- `400` — bad input
- `401` — not authenticated / invalid token
- `403` — authenticated but not admin
- `404` — resource not found
- `409` — conflict (duplicate)
- `204` — success with no body

---

## 1. Authentication

### POST `/api/v1/admin/auth/login/`
Login with email and password. Returns JWT tokens.

**Request Body (JSON):**
```json
{
  "email": "admin@example.com",
  "password": "your_password"
}
```

**Response `200`:**
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "superadmin",
    "fullName": "علی احمدی",
    "avatar": null,
    "isActive": true,
    "lastLogin": "2024-01-15T10:30:00+03:30",
    "createdAt": "2024-01-01T00:00:00+03:30"
  }
}
```

`role` values: `"superadmin"` | `"admin"` | `"editor"` | `"support"`

**Errors:**
| code | status | meaning |
|------|--------|---------|
| `MISSING_CREDENTIALS` | 400 | email یا password خالی |
| `USER_NOT_FOUND` | 401 | ایمیل وجود ندارد |
| `INVALID_PASSWORD` | 401 | رمز اشتباه |
| `NOT_ADMIN` | 403 | کاربر is_staff نیست |
| `INACTIVE` | 401 | حساب غیرفعال |

---

### POST `/api/v1/admin/auth/refresh/`
Refresh access token.

**Request Body (JSON):**
```json
{ "refresh": "eyJhbGci..." }
```

**Response `200`:**
```json
{ "access": "eyJhbGci..." }
```

---

### POST `/api/v1/admin/auth/logout/`
Blacklist refresh token (invalidate session).

**Headers:** `Authorization: Bearer <access_token>`

**Request Body (JSON):**
```json
{ "refresh": "eyJhbGci..." }
```

**Response:** `204 No Content`

---

## 2. Dashboard

### GET `/api/v1/admin/dashboard/stats/`
Key metrics for current month vs previous month.

**Response `200`:**
```json
{
  "totalRevenue": 12500000,
  "revenueGrowth": 15.3,
  "totalOrders": 342,
  "ordersGrowth": 8.7,
  "totalProducts": 128,
  "productsGrowth": 2.1,
  "totalUsers": 956,
  "usersGrowth": 5.0,
  "pendingOrders": 14,
  "lowStockProducts": 3,
  "newMessages": 7,
  "pendingReviews": 12
}
```

- `*Growth` — درصد رشد نسبت به ماه قبل (می‌تواند منفی باشد)
- `lowStockProducts` — محصولاتی که stock ≤ 5 دارند و فعال هستند

---

### GET `/api/v1/admin/dashboard/revenue/?period=month`
Revenue chart data.

**Query Params:**
| param | values | default |
|-------|--------|---------|
| `period` | `week` \| `month` \| `year` | `month` |

**Response `200` (array):**
```json
[
  { "label": "فروردین", "revenue": 3200000, "orders": 45 },
  { "label": "اردیبهشت", "revenue": 4100000, "orders": 58 },
  ...
]
```

- `period=week` → 7 آیتم با label روز فارسی (شنبه، یکشنبه، ...)
- `period=month` → 12 آیتم با label ماه فارسی
- `period=year` → 3 آیتم با label سال میلادی

---

### GET `/api/v1/admin/dashboard/top-products/`
Top 5 products by number of orders.

**Response `200` (array, max 5 items):**
```json
[
  {
    "id": 12,
    "name": "لپ‌تاپ ایسوس مدل X",
    "image": "http://domain.com/media/products/laptop.jpg",
    "sales": 87,
    "revenue": 43500000
  }
]
```

---

### GET `/api/v1/admin/dashboard/recent-orders/`
Last 5 orders.

**Response `200` (array, max 5 items):**
```json
[
  {
    "id": 301,
    "orderNumber": "ORD-20240115-0301",
    "customerName": "محمد رضایی",
    "total": 2350000,
    "status": "pending",
    "createdAt": "2024-01-15T09:15:00+03:30"
  }
]
```

---

## 3. Products

### GET `/api/v1/admin/products/`
Paginated list of products with filters.

**Query Params:**
| param | type | description |
|-------|------|-------------|
| `search` | string | جستجو در نام محصول |
| `category` | integer | فیلتر بر اساس ID دسته‌بندی |
| `isActive` | `true` \| `false` | وضعیت فعال |
| `isFeatured` | `true` | فقط محصولات ویژه |
| `lowStock` | `true` | موجودی کمتر یا مساوی min_stock |
| `ordering` | string | `createdAt`, `-createdAt`, `name`, `-name`, `price`, `-price` |
| `page` | integer | شماره صفحه (default: 1) |
| `pageSize` | integer | تعداد در صفحه (default: 20, max: 100) |

**Response `200`:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "لپ‌تاپ ایسوس",
      "slug": "laptop-asus",
      "sku": "ASUS-001",
      "description": "توضیحات کامل...",
      "shortDescription": "توضیحات کوتاه",
      "price": 25000000,
      "comparePrice": 28000000,
      "costPrice": 20000000,
      "stock": 15,
      "minStock": 3,
      "weight": 2.5,
      "categoryId": 4,
      "categoryName": "لپ‌تاپ",
      "tags": ["gaming", "laptop"],
      "images": [
        {
          "id": 1,
          "url": "http://domain.com/media/products/img1.jpg",
          "alt": "",
          "isPrimary": true,
          "order": 0
        }
      ],
      "variants": [
        { "id": 1, "name": "مشکی", "value": "#000000", "stock": null }
      ],
      "attributes": [
        { "id": 1, "name": "RAM", "value": "16GB", "unit": null }
      ],
      "isActive": true,
      "isFeatured": false,
      "isNew": true,
      "isSale": false,
      "rating": 4.5,
      "reviewCount": 23,
      "salesCount": 87,
      "createdAt": "2024-01-01T00:00:00+03:30"
    }
  ],
  "count": 128,
  "next": null,
  "previous": null
}
```

---

### POST `/api/v1/admin/products/`
Create new product.

**Content-Type:** `multipart/form-data`

**Request Fields:**
| field | type | required | description |
|-------|------|----------|-------------|
| `name` | string | ✅ | نام محصول |
| `categoryId` | integer | ✅ | ID دسته‌بندی |
| `price` | number | ✅ | قیمت (تومان) |
| `slug` | string | — | اگر خالی باشد null ذخیره می‌شود |
| `sku` | string | — | کد محصول |
| `description` | string | — | توضیحات کامل |
| `shortDescription` | string | — | توضیحات کوتاه |
| `comparePrice` | number | — | قیمت قبل از تخفیف |
| `costPrice` | number | — | قیمت خرید |
| `stock` | integer | — | موجودی (default: 0) |
| `minStock` | integer | — | حداقل موجودی (default: 0) |
| `weight` | number | — | وزن (کیلوگرم) |
| `tags` | JSON string | — | آرایه تگ‌ها: `'["تگ۱","تگ۲"]'` |
| `isActive` | boolean | — | default: true |
| `isFeatured` | boolean | — | default: false |
| `isNew` | boolean | — | default: false |
| `isSale` | boolean | — | default: false |
| `image` | file | — | تصویر اصلی محصول |

**Response `201`:** همان ساختار آبجکت محصول بالا

---

### GET `/api/v1/admin/products/{id}/`
Get single product detail.

**Response `200`:** همان ساختار آبجکت محصول

---

### PATCH `/api/v1/admin/products/{id}/`
Update product fields (partial update).

**Content-Type:** `multipart/form-data` یا `application/json`

تمام فیلدهای POST قابل ارسال است. فقط فیلدهایی که ارسال شوند آپدیت می‌شوند.

**Response `200`:** ساختار محصول آپدیت‌شده

---

### DELETE `/api/v1/admin/products/{id}/`
Delete product.

**Response:** `204 No Content`

---

### POST `/api/v1/admin/products/{id}/toggle-active/`
Toggle `isActive` status.

**Response `200`:**
```json
{ "isActive": false }
```

---

### POST `/api/v1/admin/products/{id}/toggle-featured/`
Toggle `isFeatured` status.

**Response `200`:**
```json
{ "isFeatured": true }
```

---

### POST `/api/v1/admin/products/bulk-delete/`
Delete multiple products.

**Request Body (JSON):**
```json
{ "ids": [1, 2, 3] }
```

**Response `200`:**
```json
{ "deleted": 3 }
```

---

## 4. Categories

### GET `/api/v1/admin/categories/`
Paginated list.

**Query Params:** `page`, `pageSize`

**Response `200`:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "لپ‌تاپ",
      "slug": "laptop",
      "description": "...",
      "image": "http://domain.com/media/categories/laptop.jpg",
      "parentId": null,
      "isActive": true,
      "order": 0,
      "productCount": 45
    }
  ],
  "count": 12,
  "next": null,
  "previous": null
}
```

---

### GET `/api/v1/admin/categories/all/`
All categories without pagination (for dropdowns).

**Response `200` (array):** همان ساختار بالا بدون pagination

---

### POST `/api/v1/admin/categories/`
Create category.

**Content-Type:** `multipart/form-data`

| field | type | required |
|-------|------|----------|
| `name` | string | ✅ |
| `slug` | string | — |
| `description` | string | — |
| `parentId` | integer | — |
| `isActive` | boolean | — (default: true) |
| `order` | integer | — (default: 0) |
| `image` | file | — |

**Response `201`:** ساختار category

---

### GET `/api/v1/admin/categories/{id}/`
**Response `200`:** ساختار category

### PATCH `/api/v1/admin/categories/{id}/`
Partial update. همان فیلدهای POST.
**Response `200`:** ساختار category

### DELETE `/api/v1/admin/categories/{id}/`
**Note:** اگر دسته‌بندی فرزند یا محصول داشته باشد `409 Conflict` برمی‌گردد.

**Response:** `204 No Content`

**Error `409`:**
```json
{ "error": { "message": "این دسته دارای زیردسته است", "code": "HAS_CHILDREN" } }
```

---

### POST `/api/v1/admin/categories/reorder/`
Reorder categories.

**Request Body (JSON):**
```json
{ "order": [3, 1, 5, 2, 4] }
```
آرایه از ID ها به ترتیب دلخواه.

**Response `200`:**
```json
{ "success": true }
```

---

## 5. Orders

### GET `/api/v1/admin/orders/`
Paginated list with filters.

**Query Params:**
| param | type | description |
|-------|------|-------------|
| `status` | string | وضعیت سفارش |
| `startDate` | ISO datetime | از تاریخ |
| `endDate` | ISO datetime | تا تاریخ |
| `page` | integer | default: 1 |
| `pageSize` | integer | default: 20 |

**Status values:** `pending` | `paid` | `processing` | `shipped` | `delivered` | `cancelled` | `refunded`

**Response `200`:**
```json
{
  "results": [
    {
      "id": 301,
      "orderNumber": "ORD-20240115-0301",
      "status": "processing",
      "paymentStatus": "paid",
      "paymentMethod": "online",
      "customer": {
        "id": 5,
        "name": "محمد رضایی",
        "email": "m.rezaei@email.com",
        "phone": "09121234567"
      },
      "items": [
        {
          "id": 1,
          "productId": 12,
          "productName": "لپ‌تاپ ایسوس",
          "productImage": "http://domain.com/media/products/img.jpg",
          "variant": "مشکی",
          "price": 25000000,
          "quantity": 1,
          "total": 25000000
        }
      ],
      "shippingAddress": {
        "fullName": "محمد رضایی",
        "phone": "09121234567",
        "province": "تهران",
        "city": "تهران",
        "address": "خیابان ولیعصر، پلاک ۱۰",
        "postalCode": "1234567890"
      },
      "subtotal": 25000000,
      "shippingCost": 50000,
      "discount": 200000,
      "tax": 0,
      "total": 24850000,
      "discountCode": "SUMMER10",
      "trackingCode": "RH12345678IR",
      "createdAt": "2024-01-15T09:15:00+03:30",
      "updatedAt": "2024-01-15T09:15:00+03:30"
    }
  ],
  "count": 342,
  "next": null,
  "previous": null
}
```

---

### GET `/api/v1/admin/orders/{id}/`
**Response `200`:** همان ساختار order (تکی)

---

### PATCH `/api/v1/admin/orders/{id}/`
Update order status or tracking code.

**Request Body (JSON):**
```json
{
  "status": "shipped",
  "trackingCode": "RH12345678IR"
}
```

هر دو فیلد اختیاری هستند.

**Response `200`:** ساختار order آپدیت‌شده

---

### POST `/api/v1/admin/orders/{id}/note/`
Add admin note to order.

**Request Body (JSON):**
```json
{ "note": "با مشتری تماس گرفته شد" }
```

**Response `200`:**
```json
{
  "id": 1,
  "author": "علی ادمین",
  "text": "با مشتری تماس گرفته شد",
  "time": "2024-01-15T10:30:00+03:30",
  "isAdmin": true
}
```

---

### POST `/api/v1/admin/orders/{id}/cancel/`
Cancel an order.

**Request Body (JSON):**
```json
{ "reason": "درخواست مشتری" }
```
`reason` اختیاری است — اگر ارسال شود به عنوان یادداشت ذخیره می‌شود.

**Response `200`:** ساختار order با `status: "cancelled"`

---

### POST `/api/v1/admin/orders/{id}/refund/`
Mark order as refunded.

**Request Body (JSON):**
```json
{ "amount": 24850000 }
```
اگر `amount` ارسال نشود، `final_total` سفارش به عنوان مبلغ استفاده می‌شود.

**Response `200`:** ساختار order با `paymentStatus: "refunded"`

---

## 6. Users

### GET `/api/v1/admin/users/`
Paginated list.

**Query Params:**
| param | type | description |
|-------|------|-------------|
| `search` | string | جستجو در نام، ایمیل، شماره تلفن |
| `isActive` | `true` \| `false` | وضعیت فعال |
| `page` | integer | |
| `pageSize` | integer | |

**Response `200`:**
```json
{
  "results": [
    {
      "id": 5,
      "fullName": "محمد رضایی",
      "email": "m.rezaei@email.com",
      "phone": "09121234567",
      "avatar": null,
      "isActive": true,
      "ordersCount": 8,
      "totalSpent": 45000000,
      "walletBalance": 150000,
      "joinedAt": "2023-06-01T00:00:00+03:30",
      "lastLogin": "2024-01-14T18:22:00+03:30"
    }
  ],
  "count": 956,
  "next": null,
  "previous": null
}
```

---

### GET `/api/v1/admin/users/{id}/`
**Response `200`:** همان ساختار user

---

### DELETE `/api/v1/admin/users/{id}/`
**Note:** نمی‌توان حساب خود ادمین را حذف کرد (error `SELF_DELETE`).

**Response:** `204 No Content`

---

### POST `/api/v1/admin/users/{id}/toggle-active/`
**Response `200`:**
```json
{ "isActive": false }
```

---

### POST `/api/v1/admin/users/{id}/wallet/`
Add or deduct from user wallet.

**Request Body (JSON):**
```json
{
  "amount": 500000,
  "description": "جایزه مسابقه"
}
```

- `amount` مثبت → شارژ کیف پول
- `amount` منفی → کسر از کیف پول

**Response `200`:**
```json
{
  "walletBalance": 650000,
  "transaction": {
    "id": 45,
    "amount": 500000,
    "description": "جایزه مسابقه",
    "createdAt": "2024-01-15T10:30:00+03:30"
  }
}
```

---

## 7. Blog

### GET `/api/v1/admin/blog/`
**Query Params:**
| param | type |
|-------|------|
| `isPublished` | `true` \| `false` |
| `isFeatured` | `true` |
| `categoryId` | integer |
| `search` | string |
| `page` | integer |
| `pageSize` | integer |

**Response `200`:**
```json
{
  "results": [
    {
      "id": 1,
      "title": "بهترین لپ‌تاپ‌های ۲۰۲۴",
      "slug": "best-laptops-2024",
      "excerpt": "در این مقاله...",
      "content": "محتوای کامل HTML...",
      "coverImage": "http://domain.com/media/blog/img.jpg",
      "categoryId": 2,
      "categoryName": "لپ‌تاپ",
      "tags": ["laptop", "review"],
      "isPublished": true,
      "isFeatured": false,
      "viewCount": 1250,
      "publishedAt": "2024-01-10T08:00:00+03:30",
      "createdAt": "2024-01-09T15:00:00+03:30"
    }
  ],
  "count": 45,
  "next": null,
  "previous": null
}
```

---

### POST `/api/v1/admin/blog/`
Create blog post.

**Content-Type:** `multipart/form-data`

| field | type | required |
|-------|------|----------|
| `title` | string | ✅ |
| `slug` | string | ✅ |
| `content` | string | ✅ |
| `image` | file | ✅ |
| `excerpt` | string | — |
| `categoryId` | integer | — |
| `tags` | JSON string | — |
| `isPublished` | boolean | — (default: false) |
| `isFeatured` | boolean | — (default: false) |

**Response `201`:** ساختار blog post

---

### GET `/api/v1/admin/blog/{id}/`
**Response `200`:** ساختار blog post

### PATCH `/api/v1/admin/blog/{id}/`
Partial update. همان فیلدها (image می‌تواند در multipart باشد).
**Response `200`:** ساختار blog post

### DELETE `/api/v1/admin/blog/{id}/`
**Response:** `204 No Content`

---

### POST `/api/v1/admin/blog/{id}/toggle-publish/`
Toggle published status.

**Response `200`:**
```json
{
  "isPublished": true,
  "publishedAt": "2024-01-15T10:30:00+03:30"
}
```

---

## 8. Banners

### GET `/api/v1/admin/banners/`
**Query Params:** `page`, `pageSize`

**Response `200`:**
```json
{
  "results": [
    {
      "id": 1,
      "title": "جشنواره تابستانه",
      "subtitle": "تخفیف تا ۵۰٪",
      "image": "http://domain.com/media/banners/banner1.jpg",
      "mobileImage": "http://domain.com/media/banners/mobile/banner1.jpg",
      "link": "/products?sale=true",
      "buttonText": "خرید کنید",
      "bannerType": "hero",
      "order": 1,
      "isActive": true,
      "startDate": "2024-06-01",
      "endDate": "2024-06-30"
    }
  ],
  "count": 8,
  "next": null,
  "previous": null
}
```

`bannerType` values: `hero` | `sidebar` | `popup` | `strip`

---

### POST `/api/v1/admin/banners/`
**Content-Type:** `multipart/form-data`

| field | type | required |
|-------|------|----------|
| `title` | string | — |
| `subtitle` | string | — |
| `image` | file | ✅ |
| `mobileImage` | file | — |
| `link` | string | — |
| `buttonText` | string | — |
| `bannerType` | string | — (default: hero) |
| `order` | integer | — |
| `isActive` | boolean | — |
| `startDate` | date (YYYY-MM-DD) | — |
| `endDate` | date (YYYY-MM-DD) | — |

**Response `201`:** ساختار banner

### GET `/api/v1/admin/banners/{id}/`
### PATCH `/api/v1/admin/banners/{id}/`
### DELETE `/api/v1/admin/banners/{id}/` → `204`

---

### POST `/api/v1/admin/banners/reorder/`
**Request Body (JSON):**
```json
{ "order": [3, 1, 2] }
```
**Response `200`:** `{ "success": true }`

---

## 9. Sliders

### GET `/api/v1/admin/sliders/`
**Query Params:** `page`, `pageSize`

**Response `200`:**
```json
{
  "results": [
    {
      "id": 1,
      "title": "اسلاید اول",
      "subtitle": "زیرعنوان",
      "image": "http://domain.com/media/sliders/slide1.jpg",
      "mobileImage": "http://domain.com/media/sliders/mobile/slide1.jpg",
      "link": "/category/laptop",
      "buttonText": "مشاهده",
      "order": 1,
      "isActive": true
    }
  ],
  "count": 5,
  "next": null,
  "previous": null
}
```

---

### POST `/api/v1/admin/sliders/`
**Content-Type:** `multipart/form-data`

| field | type | required |
|-------|------|----------|
| `title` | string | — |
| `subtitle` | string | — |
| `image` | file | ✅ |
| `mobileImage` | file | — |
| `link` | string | — |
| `buttonText` | string | — |
| `order` | integer | — |
| `isActive` | boolean | — |

**Response `201`:** ساختار slider

### PATCH `/api/v1/admin/sliders/{id}/`
### DELETE `/api/v1/admin/sliders/{id}/` → `204`

---

### POST `/api/v1/admin/sliders/reorder/`
**Request Body (JSON):** `{ "order": [2, 1, 3] }`
**Response `200`:** `{ "success": true }`

---

## 10. FAQ

### GET `/api/v1/admin/faq/categories/`
**Response `200` (array):**
```json
[
  { "id": 1, "name": "سوالات خرید", "order": 0 }
]
```

### POST `/api/v1/admin/faq/categories/`
```json
{ "name": "سوالات پرداخت", "order": 1 }
```
**Response `201`:** ساختار category

### PATCH `/api/v1/admin/faq/categories/{id}/`
### DELETE `/api/v1/admin/faq/categories/{id}/` → `204`

---

### GET `/api/v1/admin/faq/`
**Query Params:** `categoryId`, `page`, `pageSize`

**Response `200`:**
```json
{
  "results": [
    {
      "id": 1,
      "question": "چطور سفارش بدهم؟",
      "answer": "...",
      "categoryId": 1,
      "categoryName": "سوالات خرید",
      "order": 0,
      "isActive": true
    }
  ],
  "count": 25,
  "next": null,
  "previous": null
}
```

### POST `/api/v1/admin/faq/`
```json
{
  "question": "سوال جدید",
  "answer": "پاسخ سوال",
  "categoryId": 1,
  "order": 0,
  "isActive": true
}
```
**Response `201`:** ساختار FAQ

### GET `/api/v1/admin/faq/{id}/`
### PATCH `/api/v1/admin/faq/{id}/`
### DELETE `/api/v1/admin/faq/{id}/` → `204`

---

### POST `/api/v1/admin/faq/reorder/`
**Request Body (JSON):** `{ "order": [5, 2, 1, 3, 4] }`
**Response `200`:** `{ "success": true }`

---

## 11. Discounts

### GET `/api/v1/admin/discounts/`
**Query Params:**
| param | values |
|-------|--------|
| `isActive` | `true` \| `false` |
| `type` | `percentage` \| `fixed` |
| `page`, `pageSize` | |

**Response `200`:**
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
      "startDate": null,
      "endDate": "2024-06-30",
      "applicableProducts": [],
      "applicableCategories": [],
      "createdAt": null
    }
  ],
  "count": 12,
  "next": null,
  "previous": null
}
```

---

### POST `/api/v1/admin/discounts/`
```json
{
  "code": "SALE30",
  "type": "percentage",
  "value": 30,
  "minOrderAmount": 1000000,
  "maxDiscount": 500000,
  "usageLimit": 50,
  "isActive": true,
  "endDate": "2024-12-31"
}
```

`type`: `"percentage"` | `"fixed"`

**Response `201`:** ساختار discount

---

### GET `/api/v1/admin/discounts/{id}/`
**Response `200`:** ساختار discount

### PATCH `/api/v1/admin/discounts/{id}/`
فیلدهای قابل آپدیت: `value`, `minOrderAmount`, `maxDiscount`, `usageLimit`, `isActive`, `endDate`
**Response `200`:** ساختار discount

### DELETE `/api/v1/admin/discounts/{id}/` → `204`

---

### POST `/api/v1/admin/discounts/{id}/toggle-active/`
**Response `200`:**
```json
{ "isActive": false }
```

---

## 12. Messages (Contact Tickets)

### GET `/api/v1/admin/messages/`
**Query Params:**
| param | values |
|-------|--------|
| `isRead` | `true` \| `false` |
| `search` | جستجو در نام و موضوع |
| `page`, `pageSize` | |

**Response `200`:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "علی محمدی",
      "email": "ali@email.com",
      "phone": "09131234567",
      "subject": "مشکل در پرداخت",
      "message": "متن پیام کاربر...",
      "isRead": false,
      "isReplied": false,
      "reply": null,
      "repliedAt": null,
      "status": "open",
      "createdAt": "2024-01-15T08:00:00+03:30"
    }
  ],
  "count": 34,
  "next": null,
  "previous": null
}
```

`status` values: `open` | `in_progress` | `resolved`

---

### GET `/api/v1/admin/messages/{id}/`
اگر تیکت `open` باشد، خودکار به `in_progress` تغییر می‌کند.

**Response `200`:** ساختار message

---

### DELETE `/api/v1/admin/messages/{id}/` → `204`

---

### POST `/api/v1/admin/messages/{id}/reply/`
**Request Body (JSON):**
```json
{ "reply": "متن پاسخ ادمین..." }
```

وضعیت تیکت به `resolved` تغییر می‌کند.

**Response `200`:** ساختار message با `isReplied: true`

---

### POST `/api/v1/admin/messages/{id}/mark-read/`
**Response `200`:**
```json
{ "isRead": true }
```

---

### POST `/api/v1/admin/messages/bulk-delete/`
```json
{ "ids": [1, 2, 3] }
```
**Response `200`:**
```json
{ "deleted": 3 }
```

---

## 13. Reviews

### GET `/api/v1/admin/reviews/`
**Query Params:**
| param | values |
|-------|--------|
| `isApproved` | `true` \| `false` |
| `productId` | integer |
| `rating` | 1-5 |
| `page`, `pageSize` | |

**Response `200`:**
```json
{
  "results": [
    {
      "id": 1,
      "productId": 12,
      "productName": "لپ‌تاپ ایسوس",
      "userId": 5,
      "userName": "محمد رضایی",
      "rating": 4,
      "title": "محصول خوب",
      "comment": "راضی بودم از خرید...",
      "pros": ["سرعت بالا", "طراحی زیبا"],
      "cons": ["باتری ضعیف"],
      "isApproved": false,
      "isVerified": true,
      "helpfulCount": 7,
      "createdAt": "2024-01-14T20:00:00+03:30"
    }
  ],
  "count": 89,
  "next": null,
  "previous": null
}
```

`isVerified` یعنی کاربر این محصول را واقعاً خریده است.

---

### DELETE `/api/v1/admin/reviews/{id}/` → `204`

---

### POST `/api/v1/admin/reviews/{id}/approve/`
**Response `200`:**
```json
{ "isApproved": true }
```

---

### POST `/api/v1/admin/reviews/{id}/reject/`
**Response `200`:**
```json
{ "isApproved": false }
```

---

### POST `/api/v1/admin/reviews/bulk-approve/`
```json
{ "ids": [1, 2, 3] }
```
**Response `200`:**
```json
{ "approved": 3 }
```

---

## 14. Settings

### GET `/api/v1/admin/settings/site/`
**Response `200`:**
```json
{
  "siteName": "فروشگاه آنلاین",
  "siteDescription": "بهترین فروشگاه...",
  "siteKeywords": ["فروشگاه", "خرید آنلاین"],
  "logo": "http://domain.com/media/settings/logo.png",
  "favicon": "http://domain.com/media/settings/favicon.ico",
  "email": "info@shop.com",
  "phone": "021-12345678",
  "address": "تهران، خیابان ...",
  "instagram": "https://instagram.com/shop",
  "telegram": "https://t.me/shop",
  "whatsapp": "09121234567",
  "googleAnalyticsId": "G-XXXXXXXXXX",
  "googleTagManagerId": "GTM-XXXXXXX",
  "robotsTxt": "User-agent: *\nAllow: /",
  "maintenanceMode": false
}
```

---

### PATCH `/api/v1/admin/settings/site/`
**Content-Type:** `multipart/form-data`

| field | type |
|-------|------|
| `siteName` | string |
| `siteDescription` | string |
| `siteKeywords` | JSON string: `'["کلمه۱","کلمه۲"]'` |
| `email` | string |
| `phone` | string |
| `address` | string |
| `instagram` | string |
| `telegram` | string |
| `whatsapp` | string |
| `googleAnalyticsId` | string |
| `googleTagManagerId` | string |
| `robotsTxt` | string |
| `maintenanceMode` | boolean |
| `logo` | file |
| `favicon` | file |

**Response `200`:** همان ساختار GET

---

### GET `/api/v1/admin/settings/theme/`
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

### PUT `/api/v1/admin/settings/theme/`
**Request Body (JSON):** همان فیلدهای بالا (هر کدام اختیاری)

**Response `200`:** همان ساختار GET

---

### GET `/api/v1/admin/settings/seo/`
**Response `200` (array):**
```json
[
  {
    "page": "home",
    "path": "/",
    "metaTitle": "فروشگاه | صفحه اصلی",
    "metaDescription": "بهترین فروشگاه...",
    "keywords": ["خرید آنلاین", "فروشگاه"],
    "ogImage": "http://domain.com/media/og/home.jpg",
    "noIndex": false
  }
]
```

---

### POST `/api/v1/admin/settings/seo/`
Upsert SEO settings for a page (update if path exists, create if not).

**Request Body (JSON):**
```json
{
  "page": "products",
  "path": "/products",
  "metaTitle": "محصولات | فروشگاه",
  "metaDescription": "همه محصولات...",
  "keywords": ["محصول", "خرید"],
  "ogImage": "http://domain.com/og.jpg",
  "noIndex": false
}
```

**Response `200`:** همان ساختار آبجکت SEO

---

## 15. Reports

### POST `/api/v1/admin/reports/sales/`
Sales report by time period.

**Request Body (JSON):**
```json
{
  "startDate": "2024-01-01",
  "endDate": "2024-06-30",
  "groupBy": "month",
  "status": ""
}
```

| field | values | default |
|-------|--------|---------|
| `startDate` | YYYY-MM-DD | یک سال پیش |
| `endDate` | YYYY-MM-DD | امروز |
| `groupBy` | `day` \| `month` | `month` |
| `status` | order status | همه وضعیت‌ها |

**Response `200` (array):**
```json
[
  {
    "period": "فروردین 2024",
    "orders": 58,
    "revenue": 41000000,
    "averageOrderValue": 706896,
    "newCustomers": 23
  }
]
```

---

### POST `/api/v1/admin/reports/products/`
Top selling products report.

**Request Body (JSON):**
```json
{
  "startDate": "2024-01-01",
  "endDate": "2024-06-30"
}
```

**Response `200` (array, max 50):**
```json
[
  {
    "productId": 12,
    "productName": "لپ‌تاپ ایسوس",
    "category": "لپ‌تاپ",
    "unitsSold": 87,
    "revenue": 43500000,
    "returns": 0,
    "currentStock": 15
  }
]
```

---

### POST `/api/v1/admin/reports/orders/`
Full order list report with filters.

**Request Body (JSON):**
```json
{
  "startDate": "2024-01-01",
  "endDate": "2024-01-31",
  "status": "delivered"
}
```

**Response `200` (array, max 100):** همان ساختار آبجکت‌های order

---

## 16. File Upload

### POST `/api/v1/admin/upload/`
Upload an image file.

**Content-Type:** `multipart/form-data`

| field | type | required | description |
|-------|------|----------|-------------|
| `file` | file | ✅ | فایل تصویر |
| `folder` | string | — | `products` \| `blog` \| `banners` \| `sliders` \| `settings` (default: `products`) |

**Constraints:**
- Max size: **5MB**
- Allowed types: `image/jpeg`, `image/png`, `image/webp`, `image/gif`

**Response `200`:**
```json
{
  "url": "http://domain.com/media/products/a1b2c3d4e5.jpg",
  "width": null,
  "height": null,
  "size": 245760
}
```

**Errors:**
| code | meaning |
|------|---------|
| `MISSING_FILE` | فایلی ارسال نشده |
| `FILE_TOO_LARGE` | بیش از ۵ مگابایت |
| `INVALID_FORMAT` | فرمت غیرمجاز |

---

## Notes for Frontend

### Pagination
تمام endpoint های لیست‌دار ساختار یکسانی دارند:
```json
{
  "results": [...],
  "count": 342,
  "next": null,
  "previous": null
}
```

### Token Storage
- `access` token را در memory یا sessionStorage نگه دارید
- `refresh` token را در httpOnly cookie یا localStorage
- وقتی access منقضی شد (`401`)، با refresh، access جدید بگیرید
- وقتی refresh هم منقضی شد، کاربر را به صفحه لاگین هدایت کنید

### Image Upload Flow
برای آپلود تصویر در form‌های محصول یا بلاگ:
1. ابتدا `POST /api/v1/admin/upload/` با فایل
2. URL برگشتی را در فیلد `image` یا `coverImage` ذخیره کنید
3. یا مستقیماً فایل را در `multipart/form-data` همراه با بقیه فیلدها بفرستید

### Date Format
تمام تاریخ‌های ورودی به صورت `YYYY-MM-DD` و خروجی‌ها به صورت ISO 8601 هستند.
