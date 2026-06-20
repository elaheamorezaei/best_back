# آدرس‌ها و موقعیت جغرافیایی (Addresses & Geo)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** آدرس‌ها نیاز به `Authorization: Bearer {accessToken}` دارند. جستجوی جغرافیایی عمومی است.

---

## 1. لیست آدرس‌های کاربر

```
GET /addresses/
Authorization: Bearer {accessToken}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "addresses": [
      {
        "id": 1,
        "province": "تهران",
        "city": "تهران",
        "address": "خیابان ولیعصر، پلاک ۱۰",
        "plaque": "10",
        "unit": "3",
        "postalCode": "1234567890",
        "phoneNumber": "09121234567",
        "receiverType": "self",
        "receiverName": null,
        "receiverPhone": null,
        "location": {
          "lat": 35.7219,
          "lng": 51.3347
        },
        "mapAddress": "تهران، خیابان ولیعصر",
        "isDefault": true,
        "createdAt": "1403/05/10"
      }
    ],
    "total": 1
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `receiverType` | string | `"self"` = خودم \| `"other"` = شخص دیگری |
| `receiverName` | string\|null | فقط وقتی `receiverType = "other"` مقدار دارد |
| `receiverPhone` | string\|null | فقط وقتی `receiverType = "other"` مقدار دارد |
| `location` | object\|null | `{lat, lng}` — اگر روی نقشه انتخاب نشده `null` |
| `mapAddress` | string | آدرس متنی از نقشه — ممکن است خالی باشد |
| `isDefault` | boolean | آدرس پیش‌فرض |

---

## 2. ثبت آدرس جدید

```
POST /addresses/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "province": "تهران",
  "city": "تهران",
  "address": "خیابان ولیعصر، پلاک ۱۰",
  "plaque": "10",
  "unit": "3",
  "postalCode": "1234567890",
  "phoneNumber": "09121234567",
  "receiverType": "other",
  "receiverName": "رضا احمدی",
  "receiverPhone": "09351234567",
  "location": { "lat": 35.7219, "lng": 51.3347 },
  "mapAddress": "تهران، ولیعصر",
  "isDefault": false
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `province` | ✅ | نام استان |
| `city` | ✅ | نام شهر |
| `address` | ✅ | آدرس کامل (خیابان و...) |
| `plaque` | ✅ | پلاک |
| `unit` | ❌ | واحد |
| `postalCode` | ✅ | کدپستی — دقیقاً ۱۰ رقم |
| `phoneNumber` | ✅ | موبایل — باید با ۰۹ شروع شود (۱۱ رقم) |
| `receiverType` | ❌ | `"self"` (پیش‌فرض) یا `"other"` |
| `receiverName` | ✅ اگر `other` | نام گیرنده |
| `receiverPhone` | ✅ اگر `other` | موبایل گیرنده |
| `location` | ❌ | `{lat, lng}` |
| `mapAddress` | ❌ | آدرس روی نقشه |
| `isDefault` | ❌ | آیا پیش‌فرض شود — پیش‌فرض `false` |

### Response 201
```json
{
  "success": true,
  "message": "آدرس با موفقیت ثبت شد",
  "data": {
    "id": 2,
    "province": "تهران",
    "city": "تهران",
    "address": "خیابان ولیعصر، پلاک ۱۰",
    "plaque": "10",
    "unit": "3",
    "postalCode": "1234567890",
    "phoneNumber": "09121234567"
  }
}
```

### Errors
| کد | body |
|----|------|
| `422` | `{"success": false, "errors": {"province": "این فیلد الزامی است", "postalCode": "کدپستی باید ۱۰ رقم باشد"}}` |

---

## 3. ویرایش آدرس

```
PUT /addresses/{id}/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

> **Partial update:** فقط فیلدهایی که می‌خواهید تغییر دهید ارسال کنید.

### Request Body (نمونه — همه فیلدها اختیاری)
```json
{
  "city": "اصفهان",
  "address": "خیابان چهارباغ عباسی، پلاک ۵",
  "isDefault": true
}
```

### Response 200
```json
{
  "success": true,
  "message": "آدرس با موفقیت ویرایش شد"
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "آدرس یافت نشد"}` |
| `422` | `{"success": false, "errors": {"postalCode": "کدپستی باید ۱۰ رقم باشد"}}` |

---

## 4. حذف آدرس

```
DELETE /addresses/{id}/
Authorization: Bearer {accessToken}
```

### Response 200
```json
{
  "success": true,
  "message": "آدرس با موفقیت حذف شد"
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "آدرس یافت نشد"}` |

---

## 5. جستجوی آدرس روی نقشه

```
GET /geo/search/?q={query}
```

> این endpoint عمومی است (بدون احراز هویت).

### Query Parameters
| پارامتر | اجباری | توضیح |
|---------|--------|-------|
| `q` | ✅ | متن جستجو — مثال: `تهران ولیعصر` |

### Response 200
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "displayName": "ولیعصر، تهران، استان تهران، ایران",
        "lat": 35.7219,
        "lng": 51.3347
      }
    ]
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "پارامتر q الزامی است"}` |
| `503` | `{"success": false, "message": "خطا در سرویس موقعیت‌یابی"}` |
