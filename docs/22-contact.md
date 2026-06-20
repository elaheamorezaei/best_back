# تماس با ما (Contact)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** ارسال پیام نیاز به `Authorization: Bearer {accessToken}` دارد. بقیه endpointها عمومی هستند.

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. ارسال پیام تماس

```
POST /contact/submit/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "subjectId": 2,
  "name": "علی محمدی",
  "phone": "09121234567",
  "email": "ali@example.com",
  "message": "سوالی درباره گارانتی محصول دارم...",
  "orderId": 1001
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `subjectId` | ✅ | شناسه موضوع — از لیست `/contact/subjects/` |
| `name` | ✅ | نام فرستنده |
| `phone` | ✅ | شماره موبایل |
| `email` | ❌ | ایمیل |
| `message` | ✅ | متن پیام — حداقل ۲۰ کاراکتر |
| `orderId` | ❌ | شناسه سفارش مرتبط — اگر موضوع سفارش است |

### Response 201
```json
{
  "success": true,
  "message": "پیام شما با موفقیت ارسال شد. در اسرع وقت با شما تماس می‌گیریم.",
  "data": {
    "ticketId": "TKT-1403-00231",
    "subject": "گارانتی و خدمات پس از فروش",
    "createdAt": "1403/06/15"
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "موضوع انتخاب‌شده معتبر نیست", "field": "subjectId"}` |
| `422` | `{"success": false, "errors": {"message": "متن پیام باید حداقل ۲۰ کاراکتر باشد"}}` |

---

## 2. اطلاعات تماس

```
GET /contact/info/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "phone": "021-12345678",
    "mobile": "09121234567",
    "email": "support@best.ir",
    "address": "تهران، خیابان ولیعصر، پلاک ۱۰۰",
    "workingHours": "شنبه تا پنجشنبه — ۹ تا ۱۸",
    "coordinates": {
      "lat": 35.7219,
      "lng": 51.3347
    },
    "socialLinks": [
      { "platform": "instagram", "url": "https://instagram.com/best" },
      { "platform": "telegram", "url": "https://t.me/best" }
    ]
  }
}
```

---

## 3. اسلایدر صفحه تماس

```
GET /contact/slider/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "پشتیبانی ۲۴ ساعته",
        "description": "تیم پشتیبانی ما آماده پاسخگویی است",
        "image": "http://localhost:8000/media/contact/slider/1.jpg",
        "icon": "headset"
      }
    ]
  }
}
```

---

## 4. موضوعات تماس

```
GET /contact/subjects/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "subjects": [
      { "id": 1, "name": "سوال درباره محصول" },
      { "id": 2, "name": "گارانتی و خدمات پس از فروش" },
      { "id": 3, "name": "پیگیری سفارش" },
      { "id": 4, "name": "بازگشت کالا" },
      { "id": 5, "name": "سایر موارد" }
    ]
  }
}
```

---

## 5. جزئیات تیکت

```
GET /contact/tickets/{ticket_id}/
Authorization: Bearer {accessToken}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "id": "TKT-1403-00231",
    "subject": "گارانتی و خدمات پس از فروش",
    "status": "replied",
    "statusDisplay": "پاسخ داده شده",
    "createdAt": "1403/06/15",
    "messages": [
      {
        "id": 1,
        "sender": "user",
        "text": "سوالی درباره گارانتی محصول دارم...",
        "date": "1403/06/15",
        "time": "10:30"
      },
      {
        "id": 2,
        "sender": "support",
        "senderName": "پشتیبانی بست",
        "text": "سلام، گارانتی این محصول ۱۸ ماهه است...",
        "date": "1403/06/15",
        "time": "14:00"
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `status` | string | `"pending"` \| `"in_progress"` \| `"replied"` \| `"closed"` |
| `sender` | string | `"user"` \| `"support"` |

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "تیکت یافت نشد"}` |
| `403` | `{"success": false, "message": "دسترسی غیر مجاز"}` |
