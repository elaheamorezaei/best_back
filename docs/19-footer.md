# فوتر (Footer)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** عمومی (بدون احراز هویت).

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. اطلاعات فوتر

```
GET /footer/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "logo": "http://localhost:8000/media/logo.png",
    "description": "بست؛ بزرگترین فروشگاه آنلاین لوازم خانگی در ایران",
    "contact": {
      "phone": "021-12345678",
      "email": "info@best.ir",
      "address": "تهران، خیابان ولیعصر"
    },
    "socialLinks": [
      { "platform": "instagram", "url": "https://instagram.com/best", "icon": "instagram" },
      { "platform": "telegram", "url": "https://t.me/best", "icon": "telegram" },
      { "platform": "twitter", "url": "https://twitter.com/best", "icon": "twitter" }
    ],
    "columns": [
      {
        "title": "دسترسی سریع",
        "links": [
          { "text": "درباره ما", "url": "/about" },
          { "text": "تماس با ما", "url": "/contact" },
          { "text": "قوانین و مقررات", "url": "/terms" },
          { "text": "پرسش‌های متداول", "url": "/faq" }
        ]
      },
      {
        "title": "خدمات مشتریان",
        "links": [
          { "text": "راهنمای خرید", "url": "/guide/shopping" },
          { "text": "نحوه پرداخت", "url": "/guide/payment" },
          { "text": "شرایط بازگشت کالا", "url": "/guide/return" }
        ]
      }
    ],
    "badges": [
      {
        "id": 1,
        "name": "نماد اعتماد الکترونیکی",
        "image": "http://localhost:8000/media/badges/enamad.png",
        "link": "https://enamad.ir/..."
      }
    ],
    "copyright": "© ۱۴۰۳ بست — تمامی حقوق محفوظ است"
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `socialLinks` | array | لیست شبکه‌های اجتماعی |
| `columns` | array | ستون‌های لینک‌های فوتر |
| `badges` | array | نشان‌های اعتماد (مثل نماد اعتماد) |
