# ارسال و تحویل (Delivery)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها نیاز به `Authorization: Bearer {accessToken}` دارند.

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. روش‌های ارسال

```
GET /delivery/options/
Authorization: Bearer {accessToken}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "options": [
      {
        "id": 1,
        "name": "ارسال عادی پستی",
        "description": "تحویل ۳ تا ۵ روز کاری",
        "estimatedDays": 5,
        "price": 35000,
        "isFree": false,
        "freeThreshold": 2000000
      },
      {
        "id": 2,
        "name": "ارسال پیک موتوری",
        "description": "تحویل ۱ تا ۲ روز کاری",
        "estimatedDays": 2,
        "price": 80000,
        "isFree": false,
        "freeThreshold": null
      },
      {
        "id": 3,
        "name": "ارسال رایگان",
        "description": "برای سفارش‌های بالای ۲ میلیون تومان",
        "estimatedDays": 5,
        "price": 0,
        "isFree": true,
        "freeThreshold": null
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `estimatedDays` | number | تعداد روز تخمینی تحویل |
| `price` | number | هزینه ارسال به ریال |
| `isFree` | boolean | آیا این روش رایگان است |
| `freeThreshold` | number\|null | حداقل مبلغ برای ارسال رایگان — اگر ندارد `null` |

---

## 2. محاسبه هزینه ارسال

```
POST /delivery/cost/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "addressId": 1,
  "deliveryOptionId": 2,
  "cartTotal": 3500000
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `addressId` | ✅ | شناسه آدرس انتخاب‌شده |
| `deliveryOptionId` | ✅ | شناسه روش ارسال |
| `cartTotal` | ✅ | مجموع مبلغ سبد خرید (برای بررسی ارسال رایگان) |

### Response 200
```json
{
  "success": true,
  "data": {
    "deliveryOptionId": 2,
    "deliveryName": "ارسال پیک موتوری",
    "deliveryCost": 80000,
    "isFree": false,
    "estimatedDelivery": "۱ تا ۲ روز کاری",
    "totalWithDelivery": 3580000
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `deliveryCost` | number | هزینه ارسال نهایی — اگر رایگان ۰ |
| `isFree` | boolean | آیا برای این سفارش ارسال رایگان اعمال شد |
| `totalWithDelivery` | number | مجموع سبد + هزینه ارسال |

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "آدرس یافت نشد"}` |
| `404` | `{"success": false, "message": "روش ارسال یافت نشد"}` |
