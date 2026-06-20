# سفارش‌ها و پرداخت (Orders & Payment)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها نیاز به `Authorization: Bearer {accessToken}` دارند.

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. ثبت سفارش

```
POST /orders/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "addressId": 1,
  "deliveryOptionId": 2,
  "paymentMethod": "online",
  "discountCode": "BEST20",
  "giftCardCode": "GIFT-1234-5678-ABCD",
  "useWallet": true,
  "walletAmount": 200000,
  "note": "لطفاً زنگ نزنید"
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `addressId` | ✅ | شناسه آدرس |
| `deliveryOptionId` | ✅ | شناسه روش ارسال |
| `paymentMethod` | ✅ | `"online"` \| `"wallet"` \| `"mixed"` |
| `discountCode` | ❌ | کد تخفیف |
| `giftCardCode` | ❌ | کد کارت هدیه |
| `useWallet` | ❌ | استفاده از کیف پول — پیش‌فرض `false` |
| `walletAmount` | ❌ | مبلغ از کیف پول — اگر `useWallet: true` |
| `note` | ❌ | یادداشت سفارش |

### Response 201 (پرداخت آنلاین)
```json
{
  "success": true,
  "data": {
    "orderId": 1001,
    "orderCode": "ORD-1403-001001",
    "status": "pending_payment",
    "paymentMethod": "online",
    "totalAmount": 4160000,
    "discountAmount": 520000,
    "deliveryCost": 80000,
    "walletUsed": 200000,
    "payableAmount": 3520000,
    "paymentUrl": "https://payment-gateway.ir/pay/TOKEN123"
  }
}
```

### Response 201 (پرداخت با کیف پول)
```json
{
  "success": true,
  "data": {
    "orderId": 1002,
    "orderCode": "ORD-1403-001002",
    "status": "confirmed",
    "paymentMethod": "wallet",
    "totalAmount": 2000000,
    "discountAmount": 0,
    "deliveryCost": 0,
    "walletUsed": 2000000,
    "payableAmount": 0,
    "paymentUrl": null
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `status` | string | `"pending_payment"` \| `"confirmed"` |
| `paymentUrl` | string\|null | URL درگاه پرداخت — `null` اگر پرداخت با کیف پول |

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "سبد خرید خالی است"}` |
| `400` | `{"success": false, "message": "موجودی کیف پول کافی نیست"}` |
| `400` | `{"success": false, "message": "موجودی محصول کافی نیست"}` |
| `404` | `{"success": false, "message": "آدرس یافت نشد"}` |

---

## 2. جزئیات سفارش

```
GET /orders/{order_id}/
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
        "guaranteeText": "۱۸ ماه گارانتی",
        "unitPrice": 2600000,
        "discountedPrice": 2080000,
        "quantity": 2,
        "totalPrice": 4160000
      }
    ],
    "payment": {
      "method": "online",
      "subtotal": 4160000,
      "discountCode": "BEST20",
      "discountAmount": 520000,
      "deliveryCost": 80000,
      "walletUsed": 200000,
      "giftCardUsed": 0,
      "totalPaid": 3520000
    },
    "tracking": {
      "trackingCode": "12345678901234",
      "carrier": "پست پیشتاز"
    }
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `status` | string | `"pending_payment"` \| `"confirmed"` \| `"processing"` \| `"shipped"` \| `"delivered"` \| `"cancelled"` |
| `tracking` | object\|null | اطلاعات ردیابی — اگر ارسال نشده `null` |

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "سفارش یافت نشد"}` |

---

## 3. روش‌های پرداخت

```
GET /payments/methods/
Authorization: Bearer {accessToken}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "methods": [
      {
        "id": "online",
        "name": "پرداخت آنلاین",
        "description": "پرداخت از طریق درگاه بانکی",
        "isAvailable": true
      },
      {
        "id": "wallet",
        "name": "کیف پول",
        "description": "پرداخت از موجودی کیف پول",
        "isAvailable": true,
        "walletBalance": 500000
      },
      {
        "id": "mixed",
        "name": "ترکیبی",
        "description": "پرداخت با ترکیب کیف پول و درگاه بانکی",
        "isAvailable": true
      }
    ]
  }
}
```

---

## 4. تأیید پرداخت (Callback)

```
GET /payments/verify/?Authority={authority}&Status={status}
Authorization: Bearer {accessToken}
```

> این endpoint معمولاً توسط درگاه پرداخت فراخوانی می‌شود.

### Query Parameters
| پارامتر | توضیح |
|---------|-------|
| `Authority` | کد مرجع درگاه پرداخت |
| `Status` | `"OK"` \| `"NOK"` |

### Response 200 (پرداخت موفق)
```json
{
  "success": true,
  "data": {
    "orderId": 1001,
    "orderCode": "ORD-1403-001001",
    "status": "confirmed",
    "transactionId": "67890123456",
    "paidAmount": 3520000,
    "message": "پرداخت با موفقیت انجام شد"
  }
}
```

### Response 200 (پرداخت ناموفق)
```json
{
  "success": false,
  "data": {
    "orderId": 1001,
    "orderCode": "ORD-1403-001001",
    "status": "pending_payment",
    "message": "پرداخت ناموفق بود"
  }
}
```

---

## 5. پرداخت مجدد

```
POST /orders/{order_id}/retry-payment/
Authorization: Bearer {accessToken}
```

> فقط برای سفارش‌هایی که `status = "pending_payment"` است.

### Response 200
```json
{
  "success": true,
  "data": {
    "orderId": 1001,
    "paymentUrl": "https://payment-gateway.ir/pay/NEW_TOKEN"
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "این سفارش قبلاً پرداخت شده است"}` |
| `404` | `{"success": false, "message": "سفارش یافت نشد"}` |
