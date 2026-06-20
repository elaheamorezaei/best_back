# محصولات و دسته‌بندی‌ها (Products & Categories)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها عمومی هستند مگر موارد مشخص‌شده.

> **فرمت پاسخ این بخش:**  
> لیست و جزئیات محصول از `{"data": {...}}` استفاده می‌کنند (بدون `success`).  
> ویوهای اختصاصی (featured, best-sellers, ...) از `{"success": true, "data": [...]}` استفاده می‌کنند.

---

## 1. لیست محصولات

```
GET /products/
```

### Query Parameters
| پارامتر | نوع | توضیح |
|---------|-----|-------|
| `category` | number | فیلتر بر اساس ID دسته‌بندی |
| `search` | string | جستجو در نام محصول |
| `page` | number | شماره صفحه (پیش‌فرض: `1`) |

### Response 200
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "یخچال فریزر امرسان",
      "model": "N-lITE 203",
      "brand": "امرسان",
      "description": "توضیح کوتاه...",
      "price": 2600000,
      "off": 20,
      "final_price": 2080000,
      "stock": 12,
      "image": "http://localhost:8000/media/products/pic.jpg",
      "star": 4.3,
      "is_featured": true,
      "is_best_seller": false,
      "is_popular": false,
      "sales_count": 150,
      "created_at": "2024-09-01T10:00:00Z",
      "category": 1
    }
  ]
}
```

---

## 2. جزئیات محصول

```
GET /products/{id}/
```

### Response 200
```json
{
  "data": {
    "id": 1,
    "name": "یخچال فریزر امرسان دو قلو",
    "model": "N-lITE 203",
    "brand": "امرسان",
    "star": 4.3,
    "reviewCount": 28,
    "inStock": true,
    "selectedColor": "نقره‌ای",
    "images": [
      "http://localhost:8000/media/products/1.jpg",
      "http://localhost:8000/media/products/2.jpg"
    ],
    "price": 2600000,
    "off": 20,
    "colors": [
      { "name": "نقره‌ای", "hex": "#C0C0C0" },
      { "name": "مشکی", "hex": "#000000" }
    ],
    "warranties": [
      "۱۸ ماه گارانتی امرسان",
      "خدمات پس از فروش سراسر کشور"
    ],
    "features": [
      { "name": "نمایشگر دیجیتال", "value": "دارد" },
      { "name": "سیستم نوفراست", "value": "دارد" }
    ],
    "intro": [
      "این یخچال با طراحی مدرن...",
      "سیستم نوفراست پیشرفته..."
    ],
    "specs": [
      { "name": "ظرفیت", "value": "320 لیتر" },
      { "name": "رنگ", "value": "نقره‌ای" },
      { "name": "مصرف انرژی", "value": "+B" }
    ],
    "review": {
      "text": "این یخچال یکی از بهترین گزینه‌هاست...",
      "pros": ["مصرف کم برق", "طراحی شیک"],
      "cons": ["قیمت بالا"]
    },
    "isInWishlist": false,
    "isNotifyRequested": false
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `selectedColor` | string\|null | رنگ پیش‌فرض |
| `review` | object\|null | بررسی تحریریه — اگر وجود نداشت `null` |
| `isInWishlist` | boolean | اگر کاربر لاگین نکرده `false` |
| `isNotifyRequested` | boolean | اگر کاربر لاگین نکرده `false` |

### Errors
| کد | body |
|----|------|
| `404` | `{"error": {"code": 404, "message": "محصول یافت نشد"}}` |

---

## 3. دسته‌بندی‌های اصلی (صفحه اصلی)

```
GET /categories/main/
```

### Response 200
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "image": "http://localhost:8000/media/categories/fridge.jpg",
      "category": "یخچال و فریزر",
      "link": "/category/refrigerator"
    }
  ]
}
```

---

## 4. همه دسته‌بندی‌ها

```
GET /categories/
```

### Response 200
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "یخچال و فریزر",
      "slug": "refrigerator",
      "image": "http://localhost:8000/media/categories/fridge.jpg",
      "icon": "fridge",
      "is_main": true,
      "parent": null
    }
  ]
}
```

---

## 5. جزئیات دسته‌بندی

```
GET /categories/{id}/
```

### Response 200
```json
{
  "id": 1,
  "name": "یخچال و فریزر",
  "slug": "refrigerator",
  "image": "http://localhost:8000/media/categories/fridge.jpg",
  "icon": "fridge",
  "is_main": true,
  "parent": null
}
```

---

## 6. محصولات ویژه

```
GET /products/featured/
```

### Response 200
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "image": "http://localhost:8000/media/products/pic.jpg",
      "name": "یخچال فریزر امرسان",
      "model": "N-lITE 203",
      "star": 4.3,
      "price": 2600000,
      "off": 20,
      "final_price": 2080000
    }
  ]
}
```

---

## 7. پرفروش‌ترین‌ها

```
GET /products/best-sellers/
```

پاسخ مانند `featured` — همان ساختار `ProductCard`.

---

## 8. محبوب‌ترین‌ها

```
GET /products/most-popular/
```

پاسخ مانند `featured` — همان ساختار `ProductCard`.

---

## 9. محصولات مشابه

```
GET /products/{id}/similar/?limit={n}
```

### Query Parameters
| پارامتر | نوع | پیش‌فرض |
|---------|-----|---------|
| `limit` | number | `8` |

### Response 200
```json
{
  "data": {
    "items": [
      {
        "id": 2,
        "name": "یخچال الجی",
        "model": "GN-B702",
        "image": "http://localhost:8000/media/products/lg.jpg",
        "star": 4.1,
        "price": 3100000,
        "off": 0,
        "colors": [
          { "hex": "#C0C0C0" }
        ]
      }
    ]
  }
}
```

---

## 10. افزودن / حذف از علاقه‌مندی (Toggle)

```
POST /products/{product_id}/wishlist/
Authorization: Bearer {accessToken}
```

### Response 200 (اضافه شد)
```json
{
  "data": { "isInWishlist": true },
  "message": "به علاقه‌مندی‌ها اضافه شد"
}
```

### Response 200 (حذف شد)
```json
{
  "data": { "isInWishlist": false },
  "message": "از علاقه‌مندی‌ها حذف شد"
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"error": {"code": "NOT_FOUND", "message": "محصول یافت نشد"}}` |

---

## 11. اعلان موجودی (Toggle)

```
POST /products/{product_id}/notify/
Authorization: Bearer {accessToken}
```

> فقط برای محصولات ناموجود (`stock = 0`) کار می‌کند.

### Response 200 (فعال شد)
```json
{
  "data": { "isNotifyRequested": true },
  "message": "اعلان موجودی فعال شد"
}
```

### Response 200 (لغو شد)
```json
{
  "data": { "isNotifyRequested": false },
  "message": "اعلان موجودی لغو شد"
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"error": {"code": 400, "message": "محصول در انبار موجود است", "field": "product_id"}}` |
| `404` | `{"error": {"code": "NOT_FOUND", "message": "محصول یافت نشد"}}` |
