# کدهای تخفیف و کارت هدیه (Discounts & Gift Cards)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها نیاز به `Authorization: Bearer {accessToken}` دارند.

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. اعتبارسنجی کد تخفیف

```
POST /discounts/validate/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "code": "BEST20",
  "cartTotal": 3500000
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `code` | ✅ | کد تخفیف (حروف بزرگ یا کوچک) |
| `cartTotal` | ✅ | مجموع مبلغ سبد خرید به ریال |

### Response 200 (معتبر)
```json
{
  "success": true,
  "data": {
    "code": "BEST20",
    "discountType": "percent",
    "discountValue": 20,
    "maxDiscount": 500000,
    "discountAmount": 500000,
    "finalTotal": 3000000,
    "description": "۲۰٪ تخفیف — حداکثر ۵۰۰ هزار تومان"
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `discountType` | string | `"percent"` \| `"fixed"` |
| `discountValue` | number | مقدار تخفیف — اگر درصد: عدد ۱-۱۰۰ — اگر ثابت: مبلغ به ریال |
| `maxDiscount` | number\|null | سقف تخفیف به ریال — فقط برای نوع درصدی — اگر سقف ندارد `null` |
| `discountAmount` | number | مبلغ تخفیف اعمال‌شده به ریال |
| `finalTotal` | number | مبلغ نهایی پس از تخفیف |

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "کد تخفیف نامعتبر است", "code": "INVALID_CODE"}` |
| `400` | `{"success": false, "message": "این کد تخفیف منقضی شده است", "code": "EXPIRED"}` |
| `400` | `{"success": false, "message": "این کد تخفیف قبلاً استفاده شده است", "code": "ALREADY_USED"}` |
| `400` | `{"success": false, "message": "حداقل مبلغ سفارش برای استفاده از این کد تخفیف X تومان است", "code": "MIN_ORDER_NOT_MET"}` |

---

## 2. اعتبارسنجی کارت هدیه

```
POST /gift-cards/validate/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "code": "GIFT-1234-5678-ABCD",
  "cartTotal": 2000000
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `code` | ✅ | کد کارت هدیه |
| `cartTotal` | ✅ | مجموع مبلغ سبد خرید |

### Response 200 (معتبر)
```json
{
  "success": true,
  "data": {
    "code": "GIFT-1234-5678-ABCD",
    "balance": 500000,
    "usableAmount": 500000,
    "finalTotal": 1500000,
    "expiryDate": "1404/06/31"
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `balance` | number | موجودی کل کارت هدیه |
| `usableAmount` | number | مقدار قابل استفاده در این سفارش (حداکثر برابر `cartTotal`) |
| `finalTotal` | number | مبلغ نهایی پس از کسر کارت هدیه |
| `expiryDate` | string | تاریخ انقضا جلالی |

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "کارت هدیه نامعتبر است", "code": "INVALID_CARD"}` |
| `400` | `{"success": false, "message": "کارت هدیه منقضی شده است", "code": "EXPIRED"}` |
| `400` | `{"success": false, "message": "موجودی کارت هدیه تمام شده است", "code": "EMPTY_BALANCE"}` |
