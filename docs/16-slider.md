# اسلایدر (Slider)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** عمومی (بدون احراز هویت).

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. لیست اسلایدرها

```
GET /sliders/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "تخفیف ویژه تابستانه",
        "subtitle": "تا ۵۰٪ تخفیف روی لوازم خانگی",
        "image": "http://localhost:8000/media/sliders/summer.jpg",
        "mobileImage": "http://localhost:8000/media/sliders/summer-mobile.jpg",
        "link": "/offers/summer",
        "buttonText": "مشاهده پیشنهادات",
        "order": 1,
        "isActive": true
      },
      {
        "id": 2,
        "title": "محصولات جدید",
        "subtitle": null,
        "image": "http://localhost:8000/media/sliders/new.jpg",
        "mobileImage": null,
        "link": "/products/new",
        "buttonText": "خرید کنید",
        "order": 2,
        "isActive": true
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `subtitle` | string\|null | زیرعنوان — اگر ندارد `null` |
| `mobileImage` | string\|null | تصویر مخصوص موبایل — اگر ندارد از `image` استفاده کنید |
| `buttonText` | string\|null | متن دکمه — اگر ندارد `null` |
| `order` | number | ترتیب نمایش (صعودی) |
