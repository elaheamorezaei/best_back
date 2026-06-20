# اعلان‌ها (Notifications)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها نیاز به `Authorization: Bearer {accessToken}` دارند.

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. لیست اعلان‌ها

```
GET /notifications/
Authorization: Bearer {accessToken}
```

### Query Parameters
| پارامتر | نوع | مقادیر | پیش‌فرض |
|---------|-----|--------|---------|
| `isRead` | boolean | `true` \| `false` | — (همه) |
| `page` | number | — | `1` |
| `limit` | number | حداکثر ۵۰ | `15` |

### Response 200
```json
{
  "success": true,
  "data": {
    "unreadCount": 3,
    "pagination": {
      "currentPage": 1,
      "totalPages": 2,
      "totalCount": 18,
      "hasNext": true
    },
    "notifications": [
      {
        "id": 1,
        "title": "سفارش شما ارسال شد",
        "message": "سفارش شماره ORD-1403-001001 توسط پست پیشتاز ارسال شد.",
        "type": "order",
        "isRead": false,
        "createdAt": "1403/06/12",
        "createdTime": "14:30",
        "link": "/profile/orders/1001",
        "icon": "package"
      },
      {
        "id": 2,
        "title": "موجودی محصول",
        "message": "یخچال سامسونگ که دنبالش بودید موجود شد!",
        "type": "stock",
        "isRead": true,
        "createdAt": "1403/06/10",
        "createdTime": "09:15",
        "link": "/product/15",
        "icon": "bell"
      },
      {
        "id": 3,
        "title": "تخفیف ویژه",
        "message": "۳۰٪ تخفیف روی محصولات برگزیده — فقط تا فردا",
        "type": "promotion",
        "isRead": false,
        "createdAt": "1403/06/08",
        "createdTime": "11:00",
        "link": "/offers",
        "icon": "tag"
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `unreadCount` | number | تعداد کل اعلان‌های خوانده‌نشده |
| `type` | string | `"order"` \| `"stock"` \| `"promotion"` \| `"wallet"` \| `"system"` |
| `link` | string\|null | لینک مرتبط با اعلان — اگر ندارد `null` |
| `icon` | string | نام آیکون برای نمایش |

---

## 2. خواندن یک اعلان

```
POST /notifications/{notification_id}/read/
Authorization: Bearer {accessToken}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "id": 1,
    "isRead": true
  }
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "اعلان یافت نشد"}` |

---

## 3. خواندن همه اعلان‌ها

```
POST /notifications/read-all/
Authorization: Bearer {accessToken}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "updatedCount": 3
  },
  "message": "همه اعلان‌ها به عنوان خوانده‌شده علامت‌گذاری شدند"
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `updatedCount` | number | تعداد اعلان‌هایی که وضعیتشان تغییر کرد |
