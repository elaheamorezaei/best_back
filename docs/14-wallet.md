# کیف پول (Wallet)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها نیاز به `Authorization: Bearer {accessToken}` دارند.

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. اطلاعات کیف پول

```
GET /wallet/
Authorization: Bearer {accessToken}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "isActive": true,
    "balance": 750000,
    "blockedBalance": 0,
    "availableBalance": 750000,
    "iban": "IR120000000000000000000000",
    "accountOwner": "علی محمدی"
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `isActive` | boolean | آیا کیف پول فعال است |
| `balance` | number | موجودی کل به ریال |
| `blockedBalance` | number | موجودی مسدود (در انتظار تراکنش) |
| `availableBalance` | number | موجودی قابل استفاده |
| `iban` | string\|null | شماره شبای ثبت‌شده — فقط در صورت فعال بودن |

> اگر کیف پول غیرفعال باشد، `balance`, `blockedBalance`, `availableBalance`, `iban`, `accountOwner` همه `null` هستند.

---

## 2. ارسال OTP برای فعال‌سازی کیف پول

```
POST /wallet/activate/send-otp/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "phoneNumber": "09121234567"
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `phoneNumber` | ✅ | شماره موبایل برای دریافت کد |

### Response 200
```json
{
  "success": true,
  "message": "کد تأیید ارسال شد",
  "data": {
    "expiresIn": 120
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `expiresIn` | number | مدت اعتبار کد به ثانیه |

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "کیف پول قبلاً فعال شده است"}` |
| `429` | `{"success": false, "message": "درخواست بیش از حد — لطفاً چند دقیقه دیگر تلاش کنید"}` |

---

## 3. تأیید OTP و فعال‌سازی کیف پول

```
POST /wallet/activate/verify-otp/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "phoneNumber": "09121234567",
  "otp": "12345"
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `phoneNumber` | ✅ | شماره موبایل |
| `otp` | ✅ | کد دریافت‌شده — ۵ رقم |

### Response 200
```json
{
  "success": true,
  "message": "کیف پول با موفقیت فعال شد",
  "data": {
    "isActive": true,
    "balance": 0
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "کد تأیید نادرست است"}` |
| `400` | `{"success": false, "message": "کد تأیید منقضی شده است"}` |

---

## 4. افزایش موجودی (شارژ کیف پول)

```
POST /wallet/increase/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "amount": 500000
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `amount` | ✅ | مبلغ به ریال — حداقل ۱۰,۰۰۰ — حداکثر ۵۰,۰۰۰,۰۰۰ |

### Response 200
```json
{
  "success": true,
  "data": {
    "transactionId": "TXN-1403-00123",
    "amount": 500000,
    "paymentUrl": "https://payment-gateway.ir/pay/WALLET_TOKEN"
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "حداقل مبلغ شارژ ۱۰,۰۰۰ ریال است"}` |
| `400` | `{"success": false, "message": "کیف پول فعال نیست"}` |

---

## 5. تأیید پرداخت شارژ کیف پول

```
GET /wallet/increase/verify/?Authority={authority}&Status={status}
Authorization: Bearer {accessToken}
```

### Query Parameters
| پارامتر | توضیح |
|---------|-------|
| `Authority` | کد مرجع درگاه |
| `Status` | `"OK"` \| `"NOK"` |

### Response 200 (موفق)
```json
{
  "success": true,
  "data": {
    "transactionId": "TXN-1403-00123",
    "amount": 500000,
    "newBalance": 1250000,
    "message": "کیف پول با موفقیت شارژ شد"
  }
}
```

### Response 200 (ناموفق)
```json
{
  "success": false,
  "data": {
    "message": "پرداخت ناموفق بود — مبلغی از حساب شما کسر نشد"
  }
}
```

---

## 6. برداشت از کیف پول

```
POST /wallet/withdraw/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "amount": 300000,
  "iban": "IR120000000000000000000000"
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `amount` | ✅ | مبلغ درخواست برداشت به ریال |
| `iban` | ✅ | شماره شبای مقصد |

### Response 200
```json
{
  "success": true,
  "message": "درخواست برداشت با موفقیت ثبت شد",
  "data": {
    "transactionId": "WD-1403-00045",
    "amount": 300000,
    "iban": "IR120000000000000000000000",
    "estimatedTime": "۲۴ ساعت کاری",
    "newBalance": 450000
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "موجودی کافی نیست"}` |
| `400` | `{"success": false, "message": "شماره شبا نامعتبر است"}` |
| `400` | `{"success": false, "message": "کیف پول فعال نیست"}` |

---

## 7. تاریخچه تراکنش‌های کیف پول

```
GET /wallet/transactions/
Authorization: Bearer {accessToken}
```

### Query Parameters
| پارامتر | نوع | مقادیر | پیش‌فرض |
|---------|-----|--------|---------|
| `type` | string | `"deposit"` \| `"withdrawal"` \| `"purchase"` \| `"refund"` | — (همه) |
| `page` | number | — | `1` |
| `limit` | number | حداکثر ۵۰ | `15` |

### Response 200
```json
{
  "success": true,
  "data": {
    "pagination": {
      "currentPage": 1,
      "totalPages": 3,
      "totalCount": 32,
      "hasNext": true
    },
    "transactions": [
      {
        "id": 1,
        "transactionId": "TXN-1403-00123",
        "type": "deposit",
        "typeDisplay": "شارژ کیف پول",
        "amount": 500000,
        "balanceAfter": 1250000,
        "description": "شارژ از طریق درگاه بانکی",
        "date": "1403/06/10",
        "time": "10:30",
        "status": "success"
      },
      {
        "id": 2,
        "transactionId": "TXN-1403-00124",
        "type": "purchase",
        "typeDisplay": "خرید",
        "amount": -200000,
        "balanceAfter": 1050000,
        "description": "پرداخت سفارش ORD-1403-001001",
        "date": "1403/06/11",
        "time": "09:15",
        "status": "success"
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `type` | string | `"deposit"` \| `"withdrawal"` \| `"purchase"` \| `"refund"` |
| `amount` | number | مبلغ — مثبت برای واریز، منفی برای برداشت/خرید |
| `balanceAfter` | number | موجودی کیف پول پس از این تراکنش |
| `status` | string | `"success"` \| `"pending"` \| `"failed"` |
