# جستجو (Search)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها عمومی هستند (بدون احراز هویت).

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. جستجوهای پرطرفدار (Trending)

```
GET /search/trending/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "items": [
      { "id": 1, "query": "یخچال نوفراست", "count": 1250 },
      { "id": 2, "query": "جاروبرقی رباتیک", "count": 980 },
      { "id": 3, "query": "ماشین ظرفشویی بوش", "count": 875 }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `query` | string | عبارت جستجو |
| `count` | number | تعداد جستجوی این عبارت |

---

## 2. تکمیل خودکار (Autocomplete)

```
GET /search/autocomplete/?q={query}
```

### Query Parameters
| پارامتر | اجباری | توضیح |
|---------|--------|-------|
| `q` | ✅ | متن جستجو — حداقل ۲ کاراکتر |

### Response 200
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "type": "product",
        "id": 10,
        "text": "یخچال فریزر امرسان N-lITE 203",
        "image": "http://localhost:8000/media/products/pic.jpg",
        "link": "/product/10"
      },
      {
        "type": "category",
        "id": 1,
        "text": "یخچال و فریزر",
        "image": "http://localhost:8000/media/categories/fridge.jpg",
        "link": "/category/1"
      },
      {
        "type": "query",
        "id": null,
        "text": "یخچال نوفراست",
        "image": null,
        "link": "/search?q=یخچال+نوفراست"
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `type` | string | `"product"` \| `"category"` \| `"query"` |
| `id` | number\|null | شناسه — برای نوع `"query"` مقدار `null` دارد |
| `image` | string\|null | تصویر — برای نوع `"query"` مقدار `null` دارد |

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "حداقل ۲ کاراکتر وارد کنید"}` |
