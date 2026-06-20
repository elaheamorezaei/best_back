# بلاگ و مجله (Blog)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها عمومی هستند (بدون احراز هویت).

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. دسته‌بندی‌های بلاگ

```
GET /blog/categories/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": 1,
        "name": "راهنمای خرید",
        "slug": "buying-guide",
        "postCount": 15
      },
      {
        "id": 2,
        "name": "نقد و بررسی",
        "slug": "review",
        "postCount": 28
      }
    ]
  }
}
```

---

## 2. لیست مقالات بلاگ

```
GET /blog/posts/
```

### Query Parameters
| پارامتر | نوع | توضیح |
|---------|-----|-------|
| `category` | number | فیلتر بر اساس ID دسته‌بندی |
| `search` | string | جستجو در عنوان و متن |
| `page` | number | شماره صفحه — پیش‌فرض `1` |
| `limit` | number | پیش‌فرض `12` |

### Response 200
```json
{
  "success": true,
  "data": {
    "pagination": {
      "currentPage": 1,
      "totalPages": 4,
      "totalCount": 43,
      "hasNext": true
    },
    "posts": [
      {
        "id": 1,
        "title": "راهنمای خرید یخچال فریزر ۱۴۰۳",
        "slug": "buying-guide-refrigerator-1403",
        "excerpt": "در این مقاله به معرفی بهترین یخچال‌های موجود در بازار می‌پردازیم...",
        "thumbnail": "http://localhost:8000/media/blog/fridge-guide.jpg",
        "author": "تیم تحریریه بست",
        "category": {
          "id": 1,
          "name": "راهنمای خرید",
          "slug": "buying-guide"
        },
        "publishedAt": "1403/05/20",
        "readTime": 8,
        "viewCount": 2540,
        "tags": ["یخچال", "راهنمای خرید", "لوازم خانگی"]
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `readTime` | number | زمان تخمینی مطالعه (دقیقه) |
| `tags` | array | برچسب‌های مقاله |

---

## 3. جزئیات مقاله

```
GET /blog/posts/{slug}/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "راهنمای خرید یخچال فریزر ۱۴۰۳",
    "slug": "buying-guide-refrigerator-1403",
    "content": "<p>در این مقاله...</p>",
    "thumbnail": "http://localhost:8000/media/blog/fridge-guide.jpg",
    "author": "تیم تحریریه بست",
    "authorAvatar": "http://localhost:8000/media/blog/authors/team.jpg",
    "category": {
      "id": 1,
      "name": "راهنمای خرید",
      "slug": "buying-guide"
    },
    "publishedAt": "1403/05/20",
    "updatedAt": "1403/06/01",
    "readTime": 8,
    "viewCount": 2541,
    "tags": ["یخچال", "راهنمای خرید"],
    "relatedProducts": [
      {
        "id": 10,
        "name": "یخچال فریزر امرسان",
        "image": "http://localhost:8000/media/products/pic.jpg",
        "price": 2600000,
        "off": 20
      }
    ],
    "relatedPosts": [
      {
        "id": 2,
        "title": "مقایسه یخچال‌های نوفراست",
        "slug": "compare-nofrost",
        "thumbnail": "http://localhost:8000/media/blog/nofrost.jpg",
        "publishedAt": "1403/05/10"
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `content` | string | محتوای HTML مقاله |
| `relatedProducts` | array | محصولات مرتبط — ممکن است خالی باشد |
| `relatedPosts` | array | مقالات مرتبط — ممکن است خالی باشد |

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "مقاله یافت نشد"}` |

---

## 4. افزایش بازدید مقاله

```
POST /blog/posts/{slug}/view/
```

### Response 200
```json
{
  "success": true,
  "data": { "viewCount": 2542 }
}
```

---

## 5. بنرهای بلاگ

```
GET /blog/banners/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "banners": [
      {
        "id": 1,
        "image": "http://localhost:8000/media/blog/banners/1.jpg",
        "link": "/offers",
        "position": "sidebar",
        "order": 1
      }
    ]
  }
}
```

---

## 6. مقالات محبوب

```
GET /blog/popular/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": 3,
        "title": "بهترین ماشین لباسشویی‌های ایرانی",
        "slug": "best-iranian-washers",
        "thumbnail": "http://localhost:8000/media/blog/washer.jpg",
        "viewCount": 8900,
        "publishedAt": "1403/04/15"
      }
    ]
  }
}
```

---

## 7. مجله (بخش ویژه)

```
GET /blog/magazine/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "featured": {
      "id": 1,
      "title": "راهنمای خرید یخچال فریزر ۱۴۰۳",
      "slug": "buying-guide-refrigerator-1403",
      "thumbnail": "http://localhost:8000/media/blog/fridge-guide.jpg",
      "excerpt": "در این مقاله...",
      "publishedAt": "1403/05/20"
    },
    "recent": [
      {
        "id": 2,
        "title": "مقایسه یخچال‌های نوفراست",
        "slug": "compare-nofrost",
        "thumbnail": "http://localhost:8000/media/blog/nofrost.jpg",
        "publishedAt": "1403/05/10",
        "category": "نقد و بررسی"
      }
    ],
    "categories": [
      {
        "id": 1,
        "name": "راهنمای خرید",
        "slug": "buying-guide",
        "postCount": 15
      }
    ]
  }
}
```

---

## 8. جستجو در بلاگ

```
GET /blog/search/?q={query}
```

### Query Parameters
| پارامتر | اجباری | توضیح |
|---------|--------|-------|
| `q` | ✅ | عبارت جستجو — حداقل ۳ کاراکتر |
| `page` | ❌ | شماره صفحه — پیش‌فرض `1` |

### Response 200
```json
{
  "success": true,
  "data": {
    "query": "یخچال نوفراست",
    "totalCount": 8,
    "posts": [
      {
        "id": 1,
        "title": "راهنمای خرید یخچال فریزر",
        "slug": "buying-guide-refrigerator-1403",
        "excerpt": "...یخچال‌های <mark>نوفراست</mark> از نظر...",
        "thumbnail": "http://localhost:8000/media/blog/fridge.jpg",
        "publishedAt": "1403/05/20"
      }
    ]
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "حداقل ۳ کاراکتر وارد کنید"}` |
