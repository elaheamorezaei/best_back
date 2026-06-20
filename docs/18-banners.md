# بنرها (Banners)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها عمومی هستند (بدون احراز هویت).

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. بنر اصلی تخفیف‌ها

```
GET /banners/discount-main/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "حراج تابستانه",
    "subtitle": "تا ۵۰٪ تخفیف",
    "image": "http://localhost:8000/media/banners/discount-main.jpg",
    "mobileImage": "http://localhost:8000/media/banners/discount-main-mobile.jpg",
    "link": "/offers",
    "backgroundColor": "#FF6B35",
    "textColor": "#FFFFFF",
    "isActive": true
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `subtitle` | string\|null | زیرعنوان |
| `mobileImage` | string\|null | تصویر موبایل — اگر ندارد از `image` استفاده کنید |
| `backgroundColor` | string\|null | رنگ پس‌زمینه hex — اگر ندارد `null` |
| `textColor` | string\|null | رنگ متن hex |

---

## 2. بنر تک‌تایی

```
GET /banners/single/?position={position}
```

### Query Parameters
| پارامتر | نوع | توضیح |
|---------|-----|-------|
| `position` | string | موقعیت بنر — مثال: `"home_top"` \| `"home_middle"` \| `"category_top"` |

### Response 200
```json
{
  "success": true,
  "data": {
    "id": 2,
    "title": "پیشنهاد ویژه هفته",
    "image": "http://localhost:8000/media/banners/single.jpg",
    "link": "/product/10",
    "position": "home_middle",
    "isActive": true
  }
}
```

---

## 3. بنرهای دوتایی

```
GET /banners/double/?position={position}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "banners": [
      {
        "id": 3,
        "title": "یخچال‌های پرفروش",
        "image": "http://localhost:8000/media/banners/double-1.jpg",
        "link": "/category/refrigerator",
        "position": "home_double",
        "order": 1
      },
      {
        "id": 4,
        "title": "ماشین لباسشویی",
        "image": "http://localhost:8000/media/banners/double-2.jpg",
        "link": "/category/washing-machine",
        "position": "home_double",
        "order": 2
      }
    ]
  }
}
```

---

## 4. بنر فوتر

```
GET /banners/footer-main/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "id": 5,
    "title": "اپلیکیشن بست",
    "subtitle": "خرید راحت‌تر از موبایل",
    "image": "http://localhost:8000/media/banners/footer.jpg",
    "link": "/app",
    "appStoreLink": "https://apps.apple.com/...",
    "googlePlayLink": "https://play.google.com/...",
    "isActive": true
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `appStoreLink` | string\|null | لینک App Store |
| `googlePlayLink` | string\|null | لینک Google Play |
