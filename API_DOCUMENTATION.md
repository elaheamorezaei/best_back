# مستندات کامل API — بست شاپ

## اطلاعات کلی

| آیتم | مقدار |
|------|-------|
| Base URL | `http://localhost:8000` |
| Content-Type | `application/json` |
| احراز هویت | `Authorization: Bearer {accessToken}` |
| فرمت تاریخ | جلالی — مثال: `1403/06/15` |
| فرمت مبلغ | عدد صحیح (تومان) |

---

## فرمت‌های پاسخ

### موفق (اکثر endpointها)
```json
{ "success": true, "data": { ... } }
```

### خطا
```json
{ "success": false, "message": "پیام خطا" }
```

### خطای اعتبارسنجی (422)
```json
{ "success": false, "message": "خطای اعتبارسنجی", "errors": { "fieldName": "پیام خطا" } }
```

> **استثنا — Compare API:** فرمت wrapper ندارد. پاسخ موفق مستقیم `{items: [...]}` و خطا `{error: "CODE", message: "..."}` است.

> **استثنا — Products/Reviews API:** از فرمت `{"data": {...}}` بدون `success` استفاده می‌کند.

---

## فهرست endpointها

1. [احراز هویت](#-احراز-هویت)
2. [پروفایل](#-پروفایل)
3. [آدرس‌ها](#-آدرسها)
4. [موقعیت جغرافیایی](#-موقعیت-جغرافیایی)
5. [محصولات و دسته‌بندی](#-محصولات-و-دستهبندی)
6. [نظرات و سوالات](#-نظرات-و-سوالات)
7. [سبد خرید](#-سبد-خرید)
8. [ارسال و حمل‌ونقل](#-ارسال-و-حملونقل)
9. [کدهای تخفیف](#-کدهای-تخفیف)
10. [سفارش‌ها و پرداخت](#-سفارشها-و-پرداخت)
11. [پروفایل — سفارش‌ها](#-پروفایل--سفارشها)
12. [علاقه‌مندی‌ها](#-علاقهمندیها)
13. [پیام‌ها و اعلان‌ها](#-پیامها-و-اعلانها)
14. [کیف پول](#-کیف-پول)
15. [جستجو](#-جستجو)
16. [اسلایدر](#-اسلایدر)
17. [هدر / منوی مگا](#-هدر--منوی-مگا)
18. [بنرها](#-بنرها)
19. [فوتر](#-فوتر)
20. [بلاگ](#-بلاگ)
21. [درباره ما](#-درباره-ما)
22. [تماس با ما](#-تماس-با-ما)
23. [سوالات متداول (FAQ)](#-سوالات-متداول-faq)
24. [قوانین و مقررات](#-قوانین-و-مقررات)
25. [مقایسه محصولات](#-مقایسه-محصولات)

---

## 🔐 احراز هویت

### 1. بررسی شماره موبایل
```
POST /api/v1/auth/phone/
```
**Body:**
```json
{ "phoneNumber": "09121234567" }
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "isRegistered": true,
    "nextStep": "password",
    "phoneNumber": "09121234567",
    "maskedPhone": "0912***4567"
  }
}
```
> `nextStep`: اگر کاربر ثبت‌نام کرده `"password"` ، در غیر این صورت `"otp"`

**خطاها:**
- `422` — شماره موبایل نامعتبر

---

### 2. ورود با رمز عبور
```
POST /api/v1/auth/login/password/
```
**Body:**
```json
{ "phoneNumber": "09121234567", "password": "mypassword" }
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJ...",
    "refreshToken": "eyJ...",
    "expiresIn": 3600,
    "user": {
      "id": 1,
      "fullName": "علی محمدی",
      "phone": "09121234567",
      "email": "ali@example.com",
      "avatar": "http://localhost:8000/media/avatars/pic.jpg"
    }
  }
}
```
**خطاها:**
- `401` — `{"success": false, "message": "رمز عبور اشتباه است", "code": "INVALID_PASSWORD"}`
- `404` — شماره موبایل یافت نشد
- `422` — خطای اعتبارسنجی
- `429` — `{"success": false, "message": "...", "data": {"retryAfterSeconds": 300}}`

---

### 3. ارسال کد OTP
```
POST /api/v1/auth/otp/send/
```
**Body:**
```json
{ "phoneNumber": "09121234567" }
```
**پاسخ 200:**
```json
{
  "success": true,
  "message": "کد تایید ارسال شد",
  "data": {
    "maskedPhone": "0912***4567",
    "expiresInSeconds": 120,
    "canResendAfterSeconds": 60,
    "debugCode": "12345"
  }
}
```
> `debugCode` فقط در حالت `DEBUG=True` ارسال می‌شود

**خطاها:**
- `422` — شماره موبایل نامعتبر
- `429` — `{"success": false, "message": "هنوز X ثانیه ...", "data": {"retryAfterSeconds": N}}`

---

### 4. تأیید کد OTP (ورود / ثبت‌نام)
```
POST /api/v1/auth/otp/verify/
```
**Body:**
```json
{ "phoneNumber": "09121234567", "code": "12345" }
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJ...",
    "refreshToken": "eyJ...",
    "expiresIn": 3600,
    "isNewUser": false,
    "user": {
      "id": 1,
      "fullName": "علی محمدی",
      "phone": "09121234567",
      "email": "ali@example.com",
      "avatar": null
    }
  }
}
```
**خطاها:**
- `410` — `{"success": false, "message": "کد منقضی شده", "code": "EXPIRED_OTP"}`
- `422` — `{"success": false, "message": "کد اشتباه است", "code": "INVALID_OTP"}`

---

### 5. فراموشی رمز — ارسال OTP
```
POST /api/v1/auth/forgot-password/send-otp/
```
**Body:**
```json
{ "phoneNumber": "09121234567" }
```
**پاسخ 200:**
```json
{
  "success": true,
  "message": "کد تایید ارسال شد",
  "data": {
    "maskedPhone": "0912***4567",
    "expiresInSeconds": 120,
    "resetToken": "abc123def456"
  }
}
```
> `resetToken` را نگه دارید — در مرحله بعد نیاز است

**خطاها:**
- `404` — شماره موبایل ثبت نشده
- `429` — cooldown

---

### 6. فراموشی رمز — تأیید OTP
```
POST /api/v1/auth/forgot-password/verify-otp/
```
**Body:**
```json
{
  "phoneNumber": "09121234567",
  "code": "12345",
  "resetToken": "abc123def456"
}
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "verified": true,
    "changeToken": "xyz789..."
  }
}
```
> `changeToken` را نگه دارید — در مرحله بعد نیاز است

**خطاها:**
- `410` — `{"code": "EXPIRED_OTP"}` یا `{"code": "EXPIRED_RESET_TOKEN"}`
- `422` — `{"code": "INVALID_OTP"}` یا `{"code": "INVALID_RESET_TOKEN"}`

---

### 7. فراموشی رمز — تغییر رمز
```
POST /api/v1/auth/forgot-password/reset/
```
**Body:**
```json
{
  "changeToken": "xyz789...",
  "newPassword": "NewPass@123",
  "confirmPassword": "NewPass@123"
}
```
**پاسخ 200:**
```json
{
  "success": true,
  "message": "رمز عبور با موفقیت تغییر یافت",
  "data": {
    "accessToken": "eyJ...",
    "refreshToken": "eyJ..."
  }
}
```
**خطاها:**
- `410` — `{"code": "EXPIRED_CHANGE_TOKEN"}`
- `422` — `{"code": "INVALID_CHANGE_TOKEN"}` / خطای اعتبارسنجی رمز

---

### 8. خروج
```
POST /api/v1/auth/logout/
Authorization: Bearer {accessToken}
```
**Body:**
```json
{ "refreshToken": "eyJ..." }
```
**پاسخ 200:**
```json
{ "success": true, "message": "با موفقیت خارج شدید" }
```

---

### 9. تجدید توکن
```
POST /api/v1/auth/refresh/
```
**Body:**
```json
{ "refreshToken": "eyJ..." }
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJ...",
    "expiresIn": 3600
  }
}
```
**خطاها:**
- `401` — `{"success": false, "message": "توکن نامعتبر", "code": "INVALID_TOKEN"}`

---

## 👤 پروفایل

> تمام endpointهای این بخش نیاز به `Authorization: Bearer {accessToken}` دارند.

### 10. دریافت اطلاعات پروفایل
```
GET /api/v1/profile/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "fullName": "علی محمدی",
    "gender": "آقا",
    "email": "ali@example.com",
    "phone": "09121234567",
    "birthDate": "1370/05/15",
    "nationalCode": "0012345678",
    "address": "تهران، خیابان ولیعصر",
    "avatar": "http://localhost:8000/media/avatars/pic.jpg",
    "createdAt": "1403/01/10"
  }
}
```
> `gender`: `"آقا"` یا `"خانم"` یا `""`

---

### 11. ویرایش پروفایل
```
PUT /api/v1/profile/
Authorization: Bearer {accessToken}
```
**Body (همه فیلدها اختیاری):**
```json
{
  "fullName": "علی محمدی",
  "email": "ali@example.com",
  "gender": "آقا",
  "birthDate": "1370/5/15",
  "address": "تهران، خیابان ولیعصر"
}
```
**پاسخ 200:**
```json
{
  "success": true,
  "message": "اطلاعات با موفقیت ذخیره شد",
  "data": {
    "id": 1,
    "fullName": "علی محمدی",
    "gender": "آقا",
    "email": "ali@example.com",
    "birthDate": "1370/5/15",
    "address": "تهران، خیابان ولیعصر"
  }
}
```
**خطاها:**
- `422` — `{"success": false, "message": "خطای اعتبارسنجی", "errors": {"birthDate": "فرمت باید YYYY/M/D باشد"}}`

---

### 12. آپلود آواتار
```
POST /api/v1/profile/avatar/
Authorization: Bearer {accessToken}
Content-Type: multipart/form-data
```
**Body (form-data):**

| فیلد | نوع | توضیح |
|------|-----|-------|
| `avatar` | file | JPG، PNG یا WEBP — حداکثر ۲ مگابایت |

**پاسخ 200:**
```json
{
  "success": true,
  "data": { "avatarUrl": "http://localhost:8000/media/avatars/pic.jpg" }
}
```
**خطاها:**
- `400` — فایل موجود نیست / حجم بیش از ۲MB / فرمت نامعتبر

---

### 13. تغییر رمز عبور
```
PUT /api/v1/profile/password/
Authorization: Bearer {accessToken}
```
**Body:**
```json
{
  "currentPassword": "OldPass@123",
  "newPassword": "NewPass@456",
  "confirmPassword": "NewPass@456"
}
```
**پاسخ 200:**
```json
{ "success": true, "message": "رمز عبور با موفقیت تغییر یافت" }
```
**خطاها:**
- `401` — `{"success": false, "message": "رمز عبور فعلی اشتباه است", "code": "WRONG_CURRENT_PASSWORD"}`
- `422` — خطای اعتبارسنجی (رمز ضعیف، عدم تطابق)

---

## 📍 آدرس‌ها

> نیاز به احراز هویت دارد.

### 14. لیست آدرس‌ها
```
GET /api/v1/addresses/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
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
        "location": { "lat": 35.7219, "lng": 51.3347 },
        "mapAddress": "تهران، ولیعصر",
        "isDefault": true,
        "createdAt": "1403/05/10"
      }
    ],
    "total": 1
  }
}
```
> `receiverType`: `"self"` یا `"other"` — اگر `"self"` باشد `receiverName` و `receiverPhone` برابر `null`

---

### 15. ثبت آدرس جدید
```
POST /api/v1/addresses/
Authorization: Bearer {accessToken}
```
**Body:**
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
> فیلدهای اجباری: `province`، `city`، `address`، `plaque`، `postalCode`، `phoneNumber`
> اگر `receiverType` برابر `"other"` باشد: `receiverName` و `receiverPhone` هم اجباری هستند

**پاسخ 201:**
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
**خطاها:**
- `422` — `{"success": false, "errors": {"province": "این فیلد الزامی است"}}`

---

### 16. ویرایش آدرس
```
PUT /api/v1/addresses/{id}/
Authorization: Bearer {accessToken}
```
**Body (فقط فیلدهایی که تغییر می‌کنند):**
```json
{
  "city": "اصفهان",
  "isDefault": true
}
```
**پاسخ 200:**
```json
{ "success": true, "message": "آدرس با موفقیت ویرایش شد" }
```

---

### 17. حذف آدرس
```
DELETE /api/v1/addresses/{id}/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{ "success": true, "message": "آدرس با موفقیت حذف شد" }
```

---

## 🗺️ موقعیت جغرافیایی

### 18. جستجوی آدرس روی نقشه
```
GET /api/v1/geo/search/?q={query}
```
**مثال:** `GET /api/v1/geo/search/?q=تهران+ولیعصر`

**پاسخ 200:**
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

---

### 19. لیست استان‌ها
```
GET /api/v1/locations/provinces/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "provinces": [
      { "id": 1, "name": "تهران" },
      { "id": 2, "name": "اصفهان" }
    ]
  }
}
```

---

### 20. لیست شهرهای یک استان
```
GET /api/v1/locations/provinces/{province_id}/cities/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "cities": [
      { "id": 1, "name": "تهران" },
      { "id": 2, "name": "شهریار" }
    ]
  }
}
```

---

### 21. لیست شهرها (با query param)
```
GET /api/v1/locations/cities/?provinceId={id}
```
**پاسخ:** همان فرمت endpoint بالا

---

## 📦 محصولات و دسته‌بندی

> این بخش از فرمت `{"data": {...}}` (بدون `success`) استفاده می‌کند.

### 22. لیست محصولات
```
GET /api/v1/products/
```
**Query Params:**

| پارامتر | نوع | توضیح |
|---------|-----|-------|
| `category` | number | فیلتر بر اساس ID دسته‌بندی |
| `search` | string | جستجو در نام |
| `page` | number | شماره صفحه |

**پاسخ 200:**
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "یخچال فریزر",
      "model": "XR-200",
      "brand": "سامسونگ",
      "price": "2600000.00",
      "off": 20,
      "star": "4.3",
      "image": "http://localhost:8000/media/products/pic.jpg",
      "category": 1,
      "inStock": true
    }
  ]
}
```

---

### 23. جزئیات محصول
```
GET /api/v1/products/{id}/
```
**پاسخ 200:**
```json
{
  "data": {
    "id": 1,
    "name": "یخچال فریزر امرسان دو قلو",
    "model": "N-lITE 203",
    "brand": "امرسان",
    "description": "توضیحات محصول...",
    "price": 2600000,
    "off": 20,
    "finalPrice": 2080000,
    "star": 4.3,
    "inStock": true,
    "stock": 12,
    "category": { "id": 1, "name": "یخچال" },
    "images": [
      { "id": 1, "image": "http://localhost:8000/media/products/1.jpg", "order": 0 }
    ],
    "colors": [
      { "id": 1, "name": "نقره‌ای", "hex": "#C0C0C0", "isDefault": true }
    ],
    "warranties": [
      { "id": 1, "text": "۱۸ ماه گارانتی", "order": 0 }
    ],
    "specs": [
      { "name": "ظرفیت", "value": "320 لیتر", "order": 0 }
    ],
    "features": [
      { "name": "نمایشگر دیجیتال", "value": "دارد", "order": 0 }
    ],
    "introParagraphs": ["متن معرفی..."],
    "editorialReview": {
      "text": "متن بررسی تحریریه",
      "pros": ["مزیت ۱", "مزیت ۲"],
      "cons": ["معایب ۱"]
    }
  }
}
```

---

### 24. دسته‌بندی‌های اصلی (صفحه اصلی)
```
GET /api/v1/categories/main/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": 1,
        "name": "یخچال",
        "slug": "refrigerator",
        "image": "http://localhost:8000/media/categories/fridge.jpg",
        "icon": "fridge-icon"
      }
    ]
  }
}
```

---

### 25. همه دسته‌بندی‌ها
```
GET /api/v1/categories/
```

### 26. جزئیات یک دسته‌بندی
```
GET /api/v1/categories/{id}/
```

---

### 27. محصولات ویژه
```
GET /api/v1/products/featured/
```
**پاسخ 200:** `{"success": true, "data": {"products": [...]}}`

### 28. پرفروش‌ترین‌ها
```
GET /api/v1/products/best-sellers/
```
**پاسخ 200:** `{"success": true, "data": {"products": [...]}}`

### 29. محبوب‌ترین‌ها
```
GET /api/v1/products/most-popular/
```
**پاسخ 200:** `{"success": true, "data": {"products": [...]}}`

---

### 30. محصولات مشابه
```
GET /api/v1/products/{id}/similar/
```
**پاسخ 200:** `{"success": true, "data": {"products": [...]}}`

---

### 31. افزودن/حذف از علاقه‌مندی (toggle)
```
POST /api/v1/products/{product_id}/wishlist/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{ "data": { "isInWishlist": true }, "message": "به علاقه‌مندی‌ها اضافه شد" }
```

---

### 32. اعلان موجودی (toggle)
```
POST /api/v1/products/{product_id}/notify/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{ "data": { "isNotifyRequested": true }, "message": "اعلان موجودی فعال شد" }
```
> فقط برای محصولات ناموجود کار می‌کند

---

## 💬 نظرات و سوالات

### 33. لیست نظرات محصول
```
GET /api/v1/products/{product_id}/comments/
```
**پاسخ 200:** `{"data": {"comments": [...], "total": N}}`

### 34. ثبت نظر
```
POST /api/v1/products/{product_id}/comments/
Authorization: Bearer {accessToken}
```
**Body:**
```json
{
  "text": "متن نظر",
  "rating": 4,
  "pros": ["مزیت ۱"],
  "cons": ["عیب ۱"]
}
```

### 35. مفید بودن نظر
```
POST /api/v1/comments/{comment_id}/helpful/
Authorization: Bearer {accessToken}
```

### 36. لیست سوالات محصول
```
GET /api/v1/products/{product_id}/questions/
```

### 37. ثبت سوال
```
POST /api/v1/products/{product_id}/questions/
Authorization: Bearer {accessToken}
```
**Body:** `{ "text": "سوال من" }`

### 38. لیست پاسخ‌های یک سوال
```
GET /api/v1/questions/{question_id}/answers/
```

### 39. ثبت پاسخ
```
POST /api/v1/questions/{question_id}/answers/
Authorization: Bearer {accessToken}
```
**Body:** `{ "text": "پاسخ من" }`

### 40. مفید بودن پاسخ
```
POST /api/v1/answers/{answer_id}/helpful/
Authorization: Bearer {accessToken}
```

---

## 🛒 سبد خرید

> نیاز به احراز هویت دارد.

### 41. دریافت / افزودن / پاک کردن سبد
```
GET    /api/v1/cart/
POST   /api/v1/cart/
DELETE /api/v1/cart/
Authorization: Bearer {accessToken}
```

**POST Body:**
```json
{
  "productId": 1,
  "colorId": 2,
  "guaranteeId": 1,
  "quantity": 2
}
```

**GET پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "productId": 1,
        "productName": "یخچال امرسان",
        "productImage": "http://...",
        "colorName": "نقره‌ای",
        "guaranteeText": "۱۸ ماه گارانتی",
        "quantity": 2,
        "unitPrice": 2080000,
        "insuranceName": null,
        "insurancePrice": 0
      }
    ],
    "total": 4160000
  }
}
```

---

### 42. ویرایش آیتم سبد
```
PUT /api/v1/cart/items/{item_id}/
Authorization: Bearer {accessToken}
```
**Body:** `{ "quantity": 3 }`

### 43. حذف آیتم از سبد
```
DELETE /api/v1/cart/items/{item_id}/
Authorization: Bearer {accessToken}
```

### 44. انتقال آیتم (سبد اصلی ↔ ذخیره‌شده)
```
PUT /api/v1/cart/items/{item_id}/move/
Authorization: Bearer {accessToken}
```

### 45. افزودن/حذف بیمه به آیتم
```
PUT /api/v1/cart/items/{item_id}/insurance/
Authorization: Bearer {accessToken}
```
**Body:** `{ "insuranceId": 1 }` یا `{ "insuranceId": null }` برای حذف

### 46. لیست پلن‌های بیمه
```
GET /api/v1/cart/insurance-plans/
```

---

## 🚚 ارسال و حمل‌ونقل

### 47. گزینه‌های ارسال
```
GET /api/v1/delivery/options/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "options": [
      {
        "id": "normal",
        "label": "ارسال عادی",
        "cost": 30000,
        "estimatedDays": "3-5"
      },
      {
        "id": "express",
        "label": "ارسال اکسپرس",
        "cost": 60000,
        "estimatedDays": "1-2"
      }
    ]
  }
}
```

### 48. محاسبه هزینه ارسال
```
GET /api/v1/delivery/cost/?deliveryType={type}&city={city}
```
**پاسخ 200:** `{"success": true, "data": {"cost": 30000, "estimatedDays": "3-5"}}`

---

## 🎟️ کدهای تخفیف

### 49. اعتبارسنجی کد تخفیف
```
POST /api/v1/discounts/validate/
Authorization: Bearer {accessToken}
```
**Body:**
```json
{ "code": "SUMMER20", "cartTotal": 2000000 }
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "code": "SUMMER20",
    "discountAmount": 400000,
    "discountPercent": 20,
    "finalTotal": 1600000
  }
}
```

### 50. اعتبارسنجی کارت هدیه
```
POST /api/v1/gift-cards/validate/
Authorization: Bearer {accessToken}
```
**Body:** `{ "code": "GIFT-ABC123" }`

---

## 🧾 سفارش‌ها و پرداخت

> نیاز به احراز هویت دارد.

### 51. ثبت سفارش
```
POST /api/v1/orders/create/
Authorization: Bearer {accessToken}
```
**Body:**
```json
{
  "addressId": 1,
  "deliveryType": "normal",
  "deliveryDate": "1403/06/20",
  "deliverySlotId": 2,
  "paymentMethod": "online",
  "discountCode": "SUMMER20",
  "giftCardCode": ""
}
```
> `deliveryType`: `"normal"` | `"express"` | `"same_day"`
> `paymentMethod`: `"online"` | `"cod"`

**پاسخ 201 (پرداخت آنلاین):**
```json
{
  "success": true,
  "data": {
    "orderId": 5,
    "orderNumber": "ABC123DEF456",
    "paymentMethod": "online",
    "paymentToken": "xyz...",
    "paymentUrl": "/api/v1/payment/gateway/?token=xyz...",
    "amount": 2080000
  }
}
```

**پاسخ 201 (پرداخت در محل):**
```json
{
  "success": true,
  "data": {
    "orderId": 5,
    "orderNumber": "ABC123DEF456",
    "paymentMethod": "cod",
    "status": "processing"
  }
}
```

**خطاها:**
- `400` — سبد خالی / موجودی کافی نیست / آدرس الزامی
- `404` — آدرس یافت نشد

---

### 52. تأیید پرداخت آنلاین
```
POST /api/v1/payment/verify/
Authorization: Bearer {accessToken}
```
**Body:** `{ "token": "xyz..." }`

**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "orderId": 5,
    "orderNumber": "ABC123DEF456",
    "trackingCode": "TRK123456",
    "status": "processing"
  }
}
```

---

### 53. تلاش مجدد پرداخت
```
POST /api/v1/orders/{order_id}/retry-payment/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "orderId": 5,
    "orderNumber": "ABC123DEF456",
    "paymentToken": "newtoken...",
    "paymentUrl": "/api/v1/payment/gateway/?token=newtoken...",
    "amount": 2080000
  }
}
```

---

### 54. لیست سفارش‌ها
```
GET /api/v1/orders/
Authorization: Bearer {accessToken}
```
**پاسخ 200:** `{"success": true, "data": [{ سفارش‌ها }]}`

---

### 55. جزئیات سفارش
```
GET /api/v1/orders/{order_id}/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "orderNumber": "ABC123DEF456",
    "status": "processing",
    "address": {
      "province": "تهران",
      "city": "تهران",
      "fullAddress": "خیابان ولیعصر، پلاک ۱۰",
      "postalCode": "1234567890",
      "receiverName": "علی محمدی",
      "phoneNumber": "09121234567",
      "receiverPhone": ""
    },
    "deliveryType": "normal",
    "deliveryDate": "1403/06/20",
    "deliveryCost": 30000,
    "paymentMethod": "online",
    "paymentTrackingCode": "TRK123456",
    "productsTotal": 2080000,
    "insuranceTotal": 0,
    "discountAmount": 0,
    "discountCodeAmount": 0,
    "giftCardAmount": 0,
    "finalTotal": 2110000,
    "createdAt": "1403/06/15",
    "items": [
      {
        "id": 1,
        "productId": 1,
        "productName": "یخچال امرسان",
        "productImage": "http://...",
        "colorName": "نقره‌ای",
        "guaranteeText": "۱۸ ماه گارانتی",
        "quantity": 1,
        "unitPrice": 2080000,
        "insuranceName": "",
        "insurancePrice": 0
      }
    ]
  }
}
```

---

### 56. روش‌های پرداخت
```
GET /api/v1/payment/methods/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": [
    { "id": "online", "label": "پرداخت آنلاین", "description": "پرداخت از طریق درگاه بانکی" },
    { "id": "cod", "label": "پرداخت در محل", "description": "پرداخت نقدی هنگام تحویل" }
  ]
}
```

---

## 📋 پروفایل — سفارش‌ها

> نیاز به احراز هویت دارد.

### 57. لیست سفارش‌ها (پروفایل)
```
GET /api/v1/profile/orders/
Authorization: Bearer {accessToken}
```
**Query Params:**

| پارامتر | نوع | توضیح |
|---------|-----|-------|
| `status` | number | `1`=در جریان، `2`=ارسال شده، `3`=تحویل داده شده، `4`=لغو شده |
| `fromDate` | string | تاریخ شروع جلالی — مثال: `1403/01/01` |
| `toDate` | string | تاریخ پایان جلالی |
| `page` | number | پیش‌فرض: `1` |
| `limit` | number | پیش‌فرض: `10` |

**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "orders": [
      {
        "id": 5,
        "row": 1,
        "date": "1403/06/15",
        "orderNumber": "ABC123DEF456",
        "amount": "2110000 تومان",
        "status": 1,
        "statusLabel": "در حال پرداخت",
        "items": [
          {
            "productId": 1,
            "name": "یخچال امرسان",
            "image": "/media/products/pic.jpg",
            "quantity": 1
          }
        ]
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "totalPages": 3
    }
  }
}
```

---

### 58. جزئیات سفارش (پروفایل)
```
GET /api/v1/profile/orders/{order_id}/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "id": 5,
    "orderNumber": "ABC123DEF456",
    "date": "1403/06/15",
    "status": 2,
    "statusLabel": "ارسال شده",
    "items": [
      {
        "productId": 1,
        "name": "یخچال امرسان",
        "image": "/media/products/pic.jpg",
        "color": "نقره‌ای",
        "guarantee": "۱۸ ماه گارانتی",
        "quantity": 1,
        "unitPrice": 2080000
      }
    ],
    "address": {
      "province": "تهران",
      "city": "تهران",
      "fullAddress": "خیابان ولیعصر، پلاک ۱۰",
      "postalCode": "1234567890",
      "receiverName": "علی محمدی",
      "phoneNumber": "09121234567"
    },
    "payment": {
      "method": "پرداخت اینترنتی",
      "trackingCode": "TRK123456",
      "amount": 2110000,
      "paidAt": "1403/06/15"
    },
    "delivery": {
      "type": "ارسال عادی",
      "date": "1403/06/20",
      "timeSlot": "۸ تا ۱۲",
      "trackingUrl": null
    }
  }
}
```

---

## ❤️ علاقه‌مندی‌ها

> نیاز به احراز هویت دارد.

### 59. لیست علاقه‌مندی‌ها
```
GET /api/v1/profile/favorites/
Authorization: Bearer {accessToken}
```
**Query Params:** `page` (پیش‌فرض: `1`)، `limit` (پیش‌فرض: `12`)

**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "favorites": [
      {
        "id": 3,
        "productId": 1,
        "image": "http://localhost:8000/media/products/pic.jpg",
        "name": "یخچال امرسان",
        "price": 2080000,
        "oldPrice": 2600000,
        "discount": 20,
        "inStock": true,
        "addedAt": "1403/05/10"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 12,
      "total": 5,
      "totalPages": 1
    }
  }
}
```
> `oldPrice` و `discount` برابر `null` هستند اگر تخفیف نداشته باشد

---

### 60. افزودن به علاقه‌مندی‌ها
```
POST /api/v1/profile/favorites/
Authorization: Bearer {accessToken}
```
**Body:** `{ "productId": 1 }`

**پاسخ 201:**
```json
{ "success": true, "message": "به علاقه‌مندی‌ها اضافه شد" }
```
**خطاها:**
- `409` — قبلاً اضافه شده
- `404` — محصول یافت نشد

---

### 61. حذف از علاقه‌مندی‌ها
```
DELETE /api/v1/profile/favorites/{favorite_id}/
Authorization: Bearer {accessToken}
```
> `favorite_id` شناسه آیتم علاقه‌مندی است، نه `productId`

**پاسخ 200:**
```json
{ "success": true, "message": "از علاقه‌مندی‌ها حذف شد" }
```

---

## 🔔 پیام‌ها و اعلان‌ها

> نیاز به احراز هویت دارد.

### 62. لیست پیام‌ها
```
GET /api/v1/profile/messages/
Authorization: Bearer {accessToken}
```
**Query Params:**

| پارامتر | نوع | مقادیر |
|---------|-----|--------|
| `type` | string | `discount` \| `info` \| `warning` \| `system` |
| `isRead` | string | `true` \| `false` |
| `page` | number | پیش‌فرض: `1` |

**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": 1,
        "title": "تخفیف ویژه",
        "message": "۲۰٪ تخفیف برای خرید بالای ۵۰۰ هزار تومان",
        "date": "1403/06/10",
        "isRead": false,
        "type": "discount"
      }
    ],
    "unreadCount": 3,
    "pagination": {
      "page": 1,
      "total": 10,
      "totalPages": 1
    }
  }
}
```

---

### 63. علامت‌گذاری پیام به عنوان خوانده‌شده
```
PUT /api/v1/profile/messages/{message_id}/read/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{ "success": true, "message": "پیام به عنوان خوانده شده علامت‌گذاری شد" }
```

---

### 64. علامت‌گذاری همه پیام‌ها
```
PUT /api/v1/profile/messages/read-all/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{ "success": true, "message": "همه پیام‌ها خوانده شدند" }
```

---

## 💰 کیف پول

> نیاز به احراز هویت دارد.

### 65. وضعیت کیف پول
```
GET /api/v1/wallet/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "balance": 500000,
    "isActive": true,
    "transactions": [
      {
        "id": 1,
        "row": 1,
        "date": "1403/06/10",
        "trackingCode": "TRX-A1B2C3D4",
        "amount": "+500000",
        "amountLabel": "+ 500,000 تومان",
        "status": 1,
        "statusLabel": "کامل",
        "type": "deposit",
        "description": "افزایش موجودی از طریق درگاه"
      }
    ],
    "pagination": { "page": 1, "total": 15 }
  }
}
```
> `amount`: مثبت = واریز، منفی = برداشت
> `type`: `deposit` | `withdraw` | `purchase`
> `status`: `1`=کامل، `2`=برداشت، `3`=شارژ، `4`=مصرف‌شده

---

### 66. فعال‌سازی کیف پول — ارسال OTP
```
POST /api/v1/wallet/activate/send-otp/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{
  "success": true,
  "message": "کد تایید ارسال شد",
  "data": {
    "maskedPhone": "0912***4567",
    "expiresInSeconds": 120,
    "debugCode": "12345"
  }
}
```
**خطاها:**
- `400` — کیف پول قبلاً فعال است
- `429` — cooldown

---

### 67. فعال‌سازی کیف پول — تأیید OTP
```
POST /api/v1/wallet/activate/verify-otp/
Authorization: Bearer {accessToken}
```
**Body:** `{ "code": "12345" }`

**پاسخ 200:** `{"success": true, "data": {"status": 1, "message": "کیف پول شما فعال شد."}}`

**خطاها:**
- `410` — `{"success": false, "data": {"status": 3, "message": "مدت اعتبار ..."}}`
- `422` — `{"success": false, "data": {"status": 2, "message": "کد وارد شده صحیح نمی‌باشد"}}`

---

### 68. افزایش موجودی
```
POST /api/v1/wallet/increase/
Authorization: Bearer {accessToken}
```
**Body:** `{ "amount": 500000 }`

> حداقل: ۱۰۰,۰۰۰ تومان — حداکثر: ۲۰۰,۰۰۰,۰۰۰ تومان

**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "paymentUrl": "/api/v1/payment/wallet/gateway/?token=abc...",
    "token": "abc...",
    "amount": 500000,
    "expiresAt": "2024-09-05T10:30:00+00:00"
  }
}
```
**خطاها:**
- `403` — کیف پول فعال نیست
- `400` — مبلغ خارج از محدوده

---

### 69. تأیید افزایش موجودی
```
POST /api/v1/wallet/increase/verify/
Authorization: Bearer {accessToken}
```
**Body:**
```json
{
  "token": "abc...",
  "status": "success",
  "bankTrackingCode": "BANK123"
}
```
> `status`: `"success"` برای پرداخت موفق، هر مقدار دیگر = ناموفق

**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "newBalance": 1000000,
    "addedAmount": 500000,
    "trackingCode": "TRX-A1B2C3D4"
  }
}
```

---

### 70. برداشت از کیف پول
```
POST /api/v1/wallet/withdraw/
Authorization: Bearer {accessToken}
```
**Body:**
```json
{
  "amount": 200000,
  "cardNumber": "6037997612345678"
}
```
> حداقل: ۵۰,۰۰۰ — حداکثر: ۵۰,۰۰۰,۰۰۰ تومان

**پاسخ 200 (فوری — تا ۱,۰۰۰,۰۰۰ تومان):**
```json
{
  "success": true,
  "data": {
    "status": 1,
    "message": "برداشت با موفقیت انجام شد.",
    "newBalance": 300000,
    "trackingCode": "WDR-A1B2C3D4"
  }
}
```

**پاسخ 200 (در صف بررسی — بیش از ۱,۰۰۰,۰۰۰ تومان):**
```json
{
  "success": true,
  "data": {
    "status": 3,
    "message": "درخواست برداشت شما در صف بررسی است و به زودی انجام می‌شود.",
    "requestId": "WDR-A1B2C3D4"
  }
}
```

**خطاها:**
- `403` — کیف پول فعال نیست
- `422` — موجودی کافی نیست: `{"data": {"currentBalance": N, "requestedAmount": N}}`

---

### 71. تاریخچه تراکنش‌ها
```
GET /api/v1/wallet/transactions/
Authorization: Bearer {accessToken}
```
**Query Params:**

| پارامتر | نوع | توضیح |
|---------|-----|-------|
| `type` | string | `deposit` \| `withdraw` \| `purchase` |
| `fromDate` | string | تاریخ شروع جلالی |
| `toDate` | string | تاریخ پایان جلالی |
| `page` | number | پیش‌فرض: `1` |
| `limit` | number | پیش‌فرض: `10` |

**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": 1,
        "row": 1,
        "date": "1403/06/10",
        "trackingCode": "TRX-A1B2C3D4",
        "amount": "+500000",
        "amountFormatted": "+ 500,000 تومان",
        "status": 1,
        "statusLabel": "کامل",
        "type": "deposit",
        "description": "افزایش موجودی از طریق درگاه"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "totalPages": 3
    }
  }
}
```
> تفاوت با `GET /wallet`: در اینجا کلید `amountFormatted` است نه `amountLabel`

---

## 🔍 جستجو

### 72. جستجوهای پرتکرار
```
GET /api/v1/search/trending/
```
**پاسخ 200:** `{"success": true, "data": {"trending": ["یخچال", "ماشین لباسشویی", ...]}}`

### 73. پیشنهاد خودکار
```
GET /api/v1/search/autocomplete/?q={query}
```
**پاسخ 200:** `{"success": true, "data": {"suggestions": [...]}}`

---

## 🎞️ اسلایدر

### 74. اسلایدر صفحه اصلی
```
GET /api/v1/slider/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "slides": [
      {
        "id": 1,
        "image": "http://localhost:8000/media/sliders/1.jpg",
        "link": "/products/1",
        "title": "تابستان با بست",
        "order": 1
      }
    ]
  }
}
```

---

## 🗂️ هدر / منوی مگا

### 75. منوی مگا
```
GET /api/v1/header/mega-menu/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": 1,
        "name": "یخچال و فریزر",
        "slug": "refrigerator",
        "image": "http://...",
        "children": [
          { "id": 3, "name": "یخچال تک‌درب", "slug": "single-door" }
        ]
      }
    ]
  }
}
```

---

## 🖼️ بنرها

### 76. بنر تخفیف اصلی
```
GET /api/v1/banners/discount-main/
```

### 77. بنر تکی
```
GET /api/v1/banners/single/
```

### 78. بنر دوتایی
```
GET /api/v1/banners/double/
```

### 79. بنر فوتر اصلی
```
GET /api/v1/banners/footer-main/
```

همه پاسخ‌ها فرمت مشابه دارند:
```json
{
  "success": true,
  "data": {
    "image": "http://localhost:8000/media/banners/main.jpg",
    "link": "/products/featured",
    "title": "تابستان با بست"
  }
}
```

---

## 🦶 فوتر

### 80. داده‌های فوتر
```
GET /api/v1/footer/data/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "logo": "http://...",
    "description": "متن فوتر",
    "socialLinks": [
      { "platform": "instagram", "url": "https://instagram.com/best" }
    ],
    "links": [...],
    "contactInfo": { "phone": "021-12345678", "email": "info@best.com" }
  }
}
```

---

## 📰 بلاگ

### 81. دسته‌بندی‌های بلاگ
```
GET /api/v1/blog/categories/
```

### 82. لیست پست‌ها
```
GET /api/v1/blog/posts/
```
**Query Params:** `category`، `page`، `limit`

**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": 1,
        "title": "راهنمای خرید یخچال",
        "slug": "guide-buy-fridge",
        "image": "http://...",
        "summary": "خلاصه مطلب...",
        "category": "راهنمای خرید",
        "publishedAt": "1403/05/20",
        "viewCount": 1240
      }
    ],
    "pagination": { "page": 1, "total": 50, "totalPages": 5 }
  }
}
```

### 83. جزئیات پست
```
GET /api/v1/blog/posts/{post_id}/
```

### 84. افزایش بازدید پست
```
POST /api/v1/blog/posts/{post_id}/view/
```

### 85. بنرهای بلاگ
```
GET /api/v1/blog/banners/
```

### 86. پست‌های پربازدید
```
GET /api/v1/blog/popular/
```

### 87. بلاگ مجله (بنر + پست‌های ویژه)
```
GET /api/v1/blog/magazine/
```

### 88. جستجو در بلاگ
```
GET /api/v1/blog/search/?q={query}
```

---

## 🏢 درباره ما

### 89. همه اطلاعات یکجا
```
GET /api/v1/about/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "slider": { "image": "http://...", "title": "بست" },
    "story": { "paragraphs": ["..."] },
    "whyUs": [{ "title": "کیفیت بالا", "icon": "quality", "description": "..." }],
    "branches": { "src": "http://...", "branchList": [{"name": "شعبه تهران", "address": "..."}] },
    "description": { "sections": [{ "title": "...", "content": "..." }] },
    "team": [{ "name": "علی احمدی", "role": "مدیرعامل", "image": "http://..." }],
    "stats": [{ "label": "مشتری", "value": "۱۰۰,۰۰۰+" }]
  }
}
```

### 90–96. endpointهای تکی
```
GET /api/v1/about/slider/
GET /api/v1/about/story/
GET /api/v1/about/why-us/
GET /api/v1/about/branches/
GET /api/v1/about/description/
GET /api/v1/about/team/
GET /api/v1/about/stats/
```

---

## 📞 تماس با ما

### 97. ارسال فرم تماس
```
POST /api/v1/contact/submit/
```
**Body:**
```json
{
  "name": "علی احمدی",
  "email": "ali@example.com",
  "phone": "09121234567",
  "subject": "انتقاد",
  "message": "پیام من..."
}
```
**پاسخ 200:** `{"success": true, "message": "پیام شما ثبت شد", "data": {"ticketId": "TCK-ABC123"}}`

### 98. اطلاعات تماس
```
GET /api/v1/contact/info/
```

### 99. اسلایدر صفحه تماس
```
GET /api/v1/contact/slider/
```

### 100. موضوعات تماس
```
GET /api/v1/contact/subjects/
```
**پاسخ 200:** `{"success": true, "data": {"subjects": ["پیشنهاد", "انتقاد", "سوال فنی", ...]}}`

### 101. پیگیری تیکت
```
GET /api/v1/contact/tickets/{ticket_id}/
```
**پاسخ 200:** `{"success": true, "data": {"id": "TCK-ABC123", "status": "در حال بررسی", ...}}`

---

## ❓ سوالات متداول (FAQ)

### 102. دسته‌بندی‌های FAQ
```
GET /api/v1/faq/categories/
```

### 103. لیست FAQ
```
GET /api/v1/faq/
```
**Query Params:** `category`، `page`

### 104. جزئیات یک FAQ
```
GET /api/v1/faq/{faq_id}/
```

### 105. جستجو در FAQ
```
GET /api/v1/faq/search/?q={query}
```

### 106. ارسال سوال جدید
```
POST /api/v1/faq/ask/
```
**Body:** `{ "question": "متن سوال", "email": "user@example.com" }`

### 107. مفید بودن FAQ
```
POST /api/v1/faq/{faq_id}/helpful/
```

---

## 📜 قوانین و مقررات

### 108. لیست قوانین (accordion)
```
GET /api/v1/terms/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "terms": [
      {
        "id": "1",
        "question": "قوانین خرید از بست چیست؟",
        "answer": "خرید از بست مستلزم...",
        "order": 1
      }
    ],
    "lastUpdated": "1403/12/01",
    "version": "2.1"
  }
}
```

---

### 109. جزئیات یک قانون
```
GET /api/v1/terms/{term_id}/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "id": "1",
    "question": "قوانین خرید از بست چیست؟",
    "answer": "خرید از بست مستلزم...",
    "order": 1,
    "lastUpdated": "1403/12/01"
  }
}
```

---

### 110. هدر صفحه قوانین
```
GET /api/v1/terms/hero/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "title": "شرایط و قوانین بست",
    "subtitle": "لطفاً قبل از استفاده از خدمات بست...",
    "lastUpdated": "1403/12/01"
  }
}
```

---

### 111. قوانین کیف پول
```
GET /api/v1/terms/wallet/
```
**پاسخ 200:**
```json
{
  "success": true,
  "data": {
    "title": "شرایط استفاده از کیف پول",
    "sections": [
      { "id": 1, "title": "فعال‌سازی کیف پول", "content": "برای استفاده..." }
    ]
  }
}
```

---

### 112. پذیرش قوانین
```
POST /api/v1/terms/accept/
Authorization: Bearer {accessToken}
```
**پاسخ 200:**
```json
{
  "success": true,
  "message": "قوانین با موفقیت پذیرفته شد",
  "data": {
    "acceptedVersion": "2.1",
    "acceptedAt": "2024-09-05T10:30:00Z"
  }
}
```

---

## ⚖️ مقایسه محصولات

> این بخش فرمت wrapper ندارد — پاسخ مستقیم بدون `success`/`data`

### 113. لیست محصولات برای مقایسه (picker)
```
GET /api/v1/compare/products/?category={slug}&search={query}&page={n}&limit={n}
```
| پارامتر | نوع | اجباری | توضیح |
|---------|-----|--------|-------|
| `category` | string | ✅ | slug دسته‌بندی — مثال: `refrigerator` |
| `search` | string | ❌ | جستجو در نام و مدل |
| `page` | number | ❌ | پیش‌فرض: `1` |
| `limit` | number | ❌ | پیش‌فرض: `20`، حداکثر: `50` |

**پاسخ 200:**
```json
{
  "items": [
    {
      "id": 10,
      "image": "http://localhost:8000/media/products/pic.jpg",
      "name": "یخچال فریزر امرسان دو قلو",
      "model": "N-lITE 203",
      "star": 4.3,
      "price": 2600000,
      "off": 20,
      "colors": ["#5C3D2E", "#4A7C59", "#9E9E9E"],
      "specs": [
        { "name": "ظرفیت", "value": "320 لیتر" },
        { "name": "رنگ", "value": "سفید" }
      ],
      "features": [
        { "name": "نمایشگر دیجیتال", "hasFeature": true },
        { "name": "آیس‌میکر", "hasFeature": false }
      ]
    }
  ],
  "total": 45,
  "page": 1,
  "totalPages": 3
}
```

**خطاها:**
- `400` — `{"error": "MISSING_CATEGORY", "message": "پارامتر category الزامی است"}`
- `404` — `{"error": "CATEGORY_NOT_FOUND", "message": "دسته‌بندی یافت نشد"}`

---

### 114. داده مقایسه (جدول کامل)
```
GET /api/v1/compare/?ids=10,11,12
```
> حداکثر ۴ شناسه با کاما جدا شوند

**پاسخ 200:**
```json
{
  "products": [
    {
      "id": 10,
      "image": "http://...",
      "name": "یخچال امرسان A",
      "model": "N-lITE 203",
      "star": 4.3,
      "price": 2600000,
      "off": 20,
      "colors": ["#5C3D2E"],
      "specs": [
        { "name": "ظرفیت", "value": "320 لیتر" },
        { "name": "رنگ", "value": "سفید" }
      ],
      "features": [
        { "name": "نمایشگر دیجیتال", "hasFeature": true },
        { "name": "آیس‌میکر", "hasFeature": false }
      ]
    },
    {
      "id": 11,
      "specs": [
        { "name": "ظرفیت", "value": "350 لیتر" },
        { "name": "رنگ", "value": null }
      ],
      "features": [
        { "name": "نمایشگر دیجیتال", "hasFeature": true },
        { "name": "آیس‌میکر", "hasFeature": true }
      ]
    }
  ]
}
```
> **مهم:** `specs` و `features` در همه محصولات ترتیب و تعداد یکسان دارند تا ردیف‌های جدول مقایسه همراستا باشند. اگر محصولی یک spec نداشته باشد `value` برابر `null` است.

**خطاها:**
```json
{ "error": "MISSING_IDS", "message": "پارامتر ids الزامی است" }
{ "error": "INVALID_IDS", "message": "فرمت ids نامعتبر است" }
{ "error": "TOO_MANY_PRODUCTS", "message": "حداکثر ۴ محصول قابل مقایسه است" }
{ "error": "PRODUCTS_NOT_FOUND", "message": "یک یا چند محصول یافت نشد", "missingIds": [99, 101] }
```

---

### 115. متن توضیحی صفحه مقایسه
```
GET /api/v1/compare/description/?category={slug}
```
**پاسخ 200:**
```json
{
  "title": "مقایسه یخچال‌ها",
  "content": "در مقایسه بین یخچال مدل A و مدل B، اولین تفاوت...\n\nاز نظر ابعاد و وزن نیز این دو مدل دیده می‌شود..."
}
```
> پاراگراف‌ها با `\n\n` جدا شده‌اند

**خطاها:**
```json
{ "error": "MISSING_CATEGORY", "message": "پارامتر category الزامی است" }
{ "error": "CATEGORY_NOT_FOUND", "message": "دسته‌بندی یافت نشد" }
{ "error": "DESCRIPTION_NOT_FOUND", "message": "توضیحاتی برای این دسته‌بندی یافت نشد" }
```

---

## کدهای HTTP

| کد | معنی |
|----|------|
| `200` | موفق |
| `201` | ساخته شد |
| `400` | درخواست نامعتبر |
| `401` | احراز هویت ناموفق |
| `403` | دسترسی ممنوع |
| `404` | یافت نشد |
| `409` | تضاد (مثلاً محصول قبلاً در لیست علاقه‌مندی) |
| `410` | منقضی شده (OTP یا توکن) |
| `422` | خطای اعتبارسنجی |
| `429` | تعداد درخواست بیش از حد |
| `503` | سرویس خارجی در دسترس نیست |
