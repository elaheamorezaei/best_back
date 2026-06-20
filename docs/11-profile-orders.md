# سفارش‌های پروفایل (Profile Orders)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها نیاز به `Authorization: Bearer {accessToken}` دارند.

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. لیست سفارش‌های کاربر

```
GET /profile/orders/
Authorization: Bearer {accessToken}
```

### Query Parameters
| پارامتر | نوع | مقادیر | پیش‌فرض |
|---------|-----|--------|---------|
| `status` | string | `pending_payment` \| `confirmed` \| `processing` \| `shipped` \| `delivered` \| `cancelled` | — (همه) |
| `page` | number | — | `1` |
| `limit` | number | حداکثر ۵۰ | `10` |

### Response 200
```json
{
  "success": true,
  "data": {
    "pagination": {
      "currentPage": 1,
      "totalPages": 3,
      "totalCount": 25,
      "hasNext": true
    },
    "orders": [
      {
        "id": 1001,
        "orderCode": "ORD-1403-001001",
        "status": "shipped",
        "statusDisplay": "ارسال شده",
        "createdAt": "1403/06/10",
        "itemCount": 2,
        "totalAmount": 4160000,
        "thumbnail": "http://localhost:8000/media/products/pic.jpg"
      },
      {
        "id": 1000,
        "orderCode": "ORD-1403-001000",
        "status": "delivered",
        "statusDisplay": "تحویل داده شده",
        "createdAt": "1403/05/20",
        "itemCount": 1,
        "totalAmount": 1800000,
        "thumbnail": "http://localhost:8000/media/products/bosch.jpg"
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `status` | string | `pending_payment` \| `confirmed` \| `processing` \| `shipped` \| `delivered` \| `cancelled` |
| `statusDisplay` | string | نمایش فارسی وضعیت |
| `thumbnail` | string\|null | تصویر اولین محصول سفارش |

---

## 2. جزئیات سفارش از پروفایل

```
GET /profile/orders/{order_id}/
Authorization: Bearer {accessToken}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "id": 1001,
    "orderCode": "ORD-1403-001001",
    "status": "shipped",
    "statusDisplay": "ارسال شده",
    "createdAt": "1403/06/10",
    "updatedAt": "1403/06/12",
    "deliveryDate": "1403/06/14",
    "address": {
      "province": "تهران",
      "city": "تهران",
      "address": "خیابان ولیعصر، پلاک ۱۰",
      "postalCode": "1234567890",
      "receiverName": "علی محمدی",
      "phoneNumber": "09121234567"
    },
    "items": [
      {
        "id": 1,
        "productId": 10,
        "productName": "یخچال فریزر امرسان",
        "productImage": "http://localhost:8000/media/products/pic.jpg",
        "colorName": "نقره‌ای",
        "colorHex": "#C0C0C0",
        "guaranteeText": "۱۸ ماه گارانتی امرسان",
        "unitPrice": 2600000,
        "discountedPrice": 2080000,
        "quantity": 2,
        "totalPrice": 4160000
      }
    ],
    "payment": {
      "method": "online",
      "methodDisplay": "پرداخت آنلاین",
      "subtotal": 4160000,
      "discountCode": "BEST20",
      "discountAmount": 520000,
      "deliveryCost": 80000,
      "walletUsed": 200000,
      "giftCardUsed": 0,
      "totalPaid": 3520000,
      "transactionId": "67890123456"
    },
    "tracking": {
      "trackingCode": "12345678901234",
      "carrier": "پست پیشتاز",
      "trackUrl": "https://tracking.post.ir/?id=12345678901234"
    },
    "timeline": [
      {
        "status": "confirmed",
        "statusDisplay": "تأیید شده",
        "date": "1403/06/10",
        "time": "10:30"
      },
      {
        "status": "processing",
        "statusDisplay": "در حال پردازش",
        "date": "1403/06/11",
        "time": "09:00"
      },
      {
        "status": "shipped",
        "statusDisplay": "ارسال شده",
        "date": "1403/06/12",
        "time": "14:15"
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `tracking` | object\|null | اگر هنوز ارسال نشده `null` |
| `tracking.trackUrl` | string\|null | لینک ردیابی — اگر ندارد `null` |
| `timeline` | array | تاریخچه تغییر وضعیت — به ترتیب زمانی |

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "سفارش یافت نشد"}` |
| `403` | `{"success": false, "message": "دسترسی غیر مجاز"}` |
