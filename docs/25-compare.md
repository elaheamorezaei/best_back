# مقایسه محصولات (Compare)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها عمومی هستند (بدون احراز هویت).

> **فرمت پاسخ:** این بخش از فرمت خام استفاده می‌کند — **بدون** wrapper `{"success": true, "data": ...}`.  
> فرمت خطا: `{"error": "ERROR_CODE", "message": "توضیح خطا"}`

---

## 1. لیست محصولات برای مقایسه

```
GET /compare/products/?category={id}&search={q}&page={n}&limit={n}
```

### Query Parameters
| پارامتر | اجباری | نوع | توضیح |
|---------|--------|-----|-------|
| `category` | ❌ | number | فیلتر بر اساس ID دسته‌بندی |
| `search` | ❌ | string | جستجو در نام محصول |
| `page` | ❌ | number | پیش‌فرض `1` |
| `limit` | ❌ | number | پیش‌فرض `20` — حداکثر `50` |

### Response 200
```json
{
  "count": 35,
  "next": "http://localhost:8000/api/v1/compare/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 10,
      "image": "http://localhost:8000/media/products/pic.jpg",
      "name": "یخچال فریزر امرسان دو قلو",
      "model": "N-lITE 203",
      "star": 4.3,
      "price": 2600000,
      "off": 20,
      "colors": [
        { "hex": "#C0C0C0" },
        { "hex": "#000000" }
      ]
    },
    {
      "id": 11,
      "image": "http://localhost:8000/media/products/lg.jpg",
      "name": "یخچال فریزر الجی دو درب",
      "model": "GN-B702",
      "star": 4.1,
      "price": 3100000,
      "off": 0,
      "colors": [
        { "hex": "#C0C0C0" }
      ]
    }
  ]
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `star` | float | میانگین امتیاز |
| `price` | number | قیمت اصلی به ریال |
| `off` | number | درصد تخفیف — اگر تخفیف ندارد `0` |
| `colors` | array | فقط رنگ‌های hex — بدون نام |

---

## 2. مقایسه محصولات

```
GET /compare/?ids=10,11,12
```

### Query Parameters
| پارامتر | اجباری | توضیح |
|---------|--------|-------|
| `ids` | ✅ | شناسه‌های محصول جداشده با کاما — حداقل ۲ — حداکثر ۴ |

### Response 200
```json
{
  "products": [
    {
      "id": 10,
      "image": "http://localhost:8000/media/products/pic.jpg",
      "name": "یخچال فریزر امرسان دو قلو",
      "model": "N-lITE 203",
      "star": 4.3,
      "price": 2600000,
      "off": 20,
      "colors": [
        { "hex": "#C0C0C0" },
        { "hex": "#000000" }
      ],
      "specs": [
        { "name": "ظرفیت", "value": "320 لیتر" },
        { "name": "رنگ", "value": "نقره‌ای" },
        { "name": "مصرف انرژی", "value": null }
      ],
      "features": [
        { "name": "نمایشگر دیجیتال", "hasFeature": true },
        { "name": "سیستم نوفراست", "hasFeature": true },
        { "name": "سردخانه جداگانه", "hasFeature": false }
      ]
    },
    {
      "id": 11,
      "image": "http://localhost:8000/media/products/lg.jpg",
      "name": "یخچال فریزر الجی دو درب",
      "model": "GN-B702",
      "star": 4.1,
      "price": 3100000,
      "off": 0,
      "colors": [
        { "hex": "#C0C0C0" }
      ],
      "specs": [
        { "name": "ظرفیت", "value": "350 لیتر" },
        { "name": "رنگ", "value": "نقره‌ای" },
        { "name": "مصرف انرژی", "value": "+A" }
      ],
      "features": [
        { "name": "نمایشگر دیجیتال", "hasFeature": true },
        { "name": "سیستم نوفراست", "hasFeature": false },
        { "name": "سردخانه جداگانه", "hasFeature": true }
      ]
    }
  ]
}
```

### نکات مهم درباره ساختار specs و features

- **ترتیب ثابت:** همه محصولات دقیقاً همان آرایه `specs` و `features` را با همان ترتیب و نام‌ها دارند (aligned).
- **مقدار نداشتن در specs:** اگر محصولی یک مشخصه را نداشته باشد، `"value": null` برمی‌گردد.
- **مقدار نداشتن در features:** اگر محصولی یک ویژگی را نداشته باشد، `"hasFeature": false` برمی‌گردد.
- **اتحادیه مشخصات:** ترتیب ردیف‌ها بر اساس اولین ظهور نام در بین محصولات انتخاب‌شده است.

| فیلد | نوع | توضیح |
|------|-----|-------|
| `specs[].value` | string\|null | مقدار مشخصه — `null` اگر محصول این مشخصه را ندارد |
| `features[].hasFeature` | boolean | `true` اگر ویژگی وجود دارد |

### Errors
| کد | body |
|----|------|
| `400` | `{"error": "MISSING_IDS", "message": "پارامتر ids الزامی است"}` |
| `400` | `{"error": "TOO_FEW_IDS", "message": "حداقل ۲ محصول انتخاب کنید"}` |
| `400` | `{"error": "TOO_MANY_IDS", "message": "حداکثر ۴ محصول قابل مقایسه است"}` |
| `400` | `{"error": "INVALID_IDS", "message": "شناسه‌های نامعتبر: 999, 1000"}` |
| `400` | `{"error": "NOT_FOUND", "message": "برخی محصولات یافت نشدند"}` |

---

## 3. توضیحات مقایسه (بر اساس دسته‌بندی)

```
GET /compare/description/?category={id}
```

### Query Parameters
| پارامتر | اجباری | توضیح |
|---------|--------|-------|
| `category` | ✅ | شناسه دسته‌بندی |

### Response 200
```json
{
  "title": "راهنمای مقایسه یخچال فریزر",
  "content": "هنگام مقایسه یخچال فریزرها به موارد زیر توجه کنید: ظرفیت، مصرف انرژی، سیستم نوفراست و..."
}
```

> **توجه:** این endpoint نیز فرمت خام برمی‌گرداند — بدون wrapper.

### Errors
| کد | body |
|----|------|
| `400` | `{"error": "MISSING_CATEGORY", "message": "پارامتر category الزامی است"}` |
| `404` | `{"error": "NOT_FOUND", "message": "توضیحات برای این دسته‌بندی یافت نشد"}` |
