# سبد خرید (Cart)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها نیاز به `Authorization: Bearer {accessToken}` دارند.

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. مشاهده سبد خرید

```
GET /cart/
Authorization: Bearer {accessToken}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "productId": 10,
        "productName": "یخچال فریزر امرسان",
        "productImage": "http://localhost:8000/media/products/pic.jpg",
        "colorId": 2,
        "colorName": "نقره‌ای",
        "colorHex": "#C0C0C0",
        "guaranteeId": 3,
        "guaranteeText": "۱۸ ماه گارانتی امرسان",
        "unitPrice": 2600000,
        "discountedPrice": 2080000,
        "quantity": 2,
        "insurance": {
          "id": 1,
          "name": "بیمه خسارت فیزیکی",
          "price": 150000,
          "duration_months": 12,
          "coverages": ["خسارت ناشی از سقوط", "خسارت ناشی از آتش‌سوزی"]
        },
        "listType": "normal"
      }
    ],
    "savedItems": [
      {
        "id": 5,
        "productId": 20,
        "productName": "جاروبرقی بوش",
        "productImage": "http://localhost:8000/media/products/bosch.jpg",
        "colorId": null,
        "colorName": null,
        "colorHex": null,
        "guaranteeId": null,
        "guaranteeText": null,
        "unitPrice": 1800000,
        "discountedPrice": 1800000,
        "quantity": 1,
        "insurance": null,
        "listType": "saved"
      }
    ],
    "summary": {
      "subtotal": 4160000,
      "discount": 1040000,
      "total": 4160000,
      "itemCount": 2
    }
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `items` | array | اقلام فعال سبد خرید |
| `savedItems` | array | اقلام ذخیره‌شده برای بعد |
| `insurance` | object\|null | بیمه انتخاب‌شده — اگر ندارد `null` |
| `colorId` | number\|null | اگر محصول بدون انتخاب رنگ اضافه شده `null` |
| `listType` | string | `"normal"` \| `"saved"` |

---

## 2. افزودن محصول به سبد

```
POST /cart/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "productId": 10,
  "colorId": 2,
  "guaranteeId": 3,
  "quantity": 1
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `productId` | ✅ | شناسه محصول |
| `colorId` | ❌ | شناسه رنگ — اگر محصول رنگ ندارد ارسال نکنید |
| `guaranteeId` | ❌ | شناسه گارانتی |
| `quantity` | ❌ | تعداد — پیش‌فرض `1` |

### Response 201
```json
{
  "success": true,
  "message": "محصول به سبد خرید اضافه شد",
  "data": {
    "cartItemId": 1,
    "productId": 10,
    "quantity": 1
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "موجودی محصول کافی نیست"}` |
| `404` | `{"success": false, "message": "محصول یافت نشد"}` |
| `409` | `{"success": false, "message": "این محصول با همین رنگ و گارانتی در سبد موجود است"}` |

---

## 3. به‌روزرسانی آیتم سبد (تعداد)

```
PUT /cart/{item_id}/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "quantity": 3
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `quantity` | ✅ | عدد صحیح ≥ ۱ |

### Response 200
```json
{
  "success": true,
  "message": "سبد خرید به‌روزرسانی شد",
  "data": {
    "cartItemId": 1,
    "quantity": 3,
    "unitPrice": 2080000,
    "totalPrice": 6240000
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "موجودی کافی نیست"}` |
| `404` | `{"success": false, "message": "آیتم یافت نشد"}` |

---

## 4. حذف آیتم از سبد

```
DELETE /cart/{item_id}/
Authorization: Bearer {accessToken}
```

### Response 200
```json
{
  "success": true,
  "message": "آیتم از سبد خرید حذف شد"
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "آیتم یافت نشد"}` |

---

## 5. جابجایی آیتم (سبد ↔ ذخیره‌شده)

```
POST /cart/{item_id}/move/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "listType": "saved"
}
```

| فیلد | مقادیر | توضیح |
|------|--------|-------|
| `listType` | `"normal"` \| `"saved"` | مقصد جابجایی |

### Response 200
```json
{
  "success": true,
  "message": "محصول به لیست ذخیره‌شده منتقل شد",
  "data": {
    "cartItemId": 1,
    "listType": "saved"
  }
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "آیتم یافت نشد"}` |
| `400` | `{"success": false, "message": "آیتم از قبل در این لیست است"}` |

---

## 6. افزودن / حذف بیمه به آیتم

```
POST /cart/{item_id}/insurance/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body (افزودن بیمه)
```json
{
  "insuranceId": 1
}
```

### Request Body (حذف بیمه)
```json
{
  "insuranceId": null
}
```

### Response 200
```json
{
  "success": true,
  "message": "بیمه به محصول اضافه شد",
  "data": {
    "cartItemId": 1,
    "insurance": {
      "id": 1,
      "name": "بیمه خسارت فیزیکی",
      "price": 150000,
      "duration_months": 12,
      "coverages": ["خسارت ناشی از سقوط"]
    }
  }
}
```

> اگر `insuranceId: null`، فیلد `insurance` در پاسخ `null` می‌شود.

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "بیمه یافت نشد"}` |
| `404` | `{"success": false, "message": "آیتم یافت نشد"}` |

---

## 7. لیست پلن‌های بیمه

```
GET /insurance/plans/?productId={id}
Authorization: Bearer {accessToken}
```

### Query Parameters
| پارامتر | اجباری | توضیح |
|---------|--------|-------|
| `productId` | ❌ | فیلتر پلن‌ها بر اساس محصول |

### Response 200
```json
{
  "success": true,
  "data": {
    "plans": [
      {
        "id": 1,
        "name": "بیمه خسارت فیزیکی",
        "price": 150000,
        "duration_months": 12,
        "coverages": [
          "خسارت ناشی از سقوط",
          "خسارت ناشی از آتش‌سوزی",
          "خسارت ناشی از نوسان برق"
        ]
      },
      {
        "id": 2,
        "name": "بیمه کامل",
        "price": 280000,
        "duration_months": 24,
        "coverages": [
          "خسارت ناشی از سقوط",
          "دزدی",
          "خسارت ناشی از آتش‌سوزی"
        ]
      }
    ]
  }
}
```
