# Product Reviews & Questions API

Base URL: `/api/v1`

احراز هویت: هدر `Authorization: Bearer <access_token>` برای endpointهای نیازمند لاگین.

---

## فهرست Endpointها

| Method | URL | Auth | توضیح |
|--------|-----|------|-------|
| GET | `/products/{id}/comments/` | اختیاری | لیست نظرات محصول |
| POST | `/products/{id}/comments/` | اجباری | ثبت نظر جدید |
| POST | `/comments/{id}/helpful/` | اجباری | رأی به نظر |
| GET | `/products/{id}/questions/` | اختیاری | لیست پرسش‌های محصول |
| POST | `/products/{id}/questions/` | اجباری | ثبت پرسش جدید |
| POST | `/questions/{id}/answers/` | اجباری | ثبت پاسخ به پرسش |
| POST | `/answers/{id}/helpful/` | اجباری | رأی به پاسخ |

---

## نظرات (Comments)

### GET `/api/v1/products/{productId}/comments/`

لیست نظرات تأیید‌شده یک محصول به همراه خلاصه آماری.

**Auth:** اختیاری — اگر توکن ارسال شود `userVote` پر می‌شود، در غیر این صورت `null` است.

**Query Parameters:**

| Param | Type | Default | مقادیر مجاز |
|-------|------|---------|------------|
| `sort` | string | `newest` | `newest` \| `top_rated` \| `has_image` |
| `page` | integer | `1` | ≥ 1 |
| `limit` | integer | `10` | 1–100 |

**Response `200`:**
```json
{
  "data": {
    "summary": {
      "averageRating": 4.2,
      "totalCount": 85,
      "distribution": {
        "5": 41,
        "4": 28,
        "3": 10,
        "2": 4,
        "1": 2
      }
    },
    "pagination": {
      "currentPage": 1,
      "totalPages": 9,
      "hasNext": true,
      "totalCount": 85
    },
    "items": [
      {
        "id": 1,
        "userName": "سارا عیدی",
        "star": 4,
        "title": "محصول خوبی بود",
        "text": "متن نظر...",
        "pros": ["کیفیت عالی", "ارسال سریع"],
        "cons": ["بسته‌بندی ضعیف"],
        "date": "۲۸ مهر ۱۴۰۳",
        "likes": 8,
        "dislikes": 2,
        "userVote": null,
        "images": []
      }
    ]
  }
}
```

**توضیح فیلدها:**

| فیلد | نوع | توضیح |
|------|-----|-------|
| `summary.averageRating` | float | میانگین امتیاز با یک رقم اعشار |
| `summary.totalCount` | int | تعداد کل نظرات تأیید‌شده |
| `summary.distribution` | object | تعداد هر ستاره از ۱ تا ۵ |
| `pagination.totalCount` | int | همان totalCount — برای نوار صفحه‌بندی |
| `items[].title` | string | عنوان نظر (ممکن است خالی باشد) |
| `items[].pros` | `string[]` | نقاط مثبت (ممکن است خالی باشد) |
| `items[].cons` | `string[]` | نقاط منفی (ممکن است خالی باشد) |
| `items[].userVote` | `"like"` \| `"dislike"` \| `null` | رأی کاربر جاری روی این نظر |
| `items[].images` | `string[]` | آرایه URL کامل تصاویر پیوست |
| `items[].date` | string | تاریخ شمسی: `"۲۸ مهر ۱۴۰۳"` |

**نکات:**
- فقط نظرات **تأیید‌شده** در لیست عمومی نمایش داده می‌شوند.
- `summary` روی **کل** نظرات تأیید‌شده محاسبه می‌شود، نه فقط صفحه جاری.

**Response `404`:**
```json
{
  "error": { "code": "NOT_FOUND", "message": "محصول یافت نشد" }
}
```

---

### POST `/api/v1/products/{productId}/comments/`

ثبت نظر جدید. هر کاربر فقط **یک بار** می‌تواند برای هر محصول نظر ثبت کند.

**Auth:** اجباری

**Request Body (`application/json`):**
```json
{
  "star": 4,
  "text": "متن نظر کاربر",
  "title": "عنوان اختیاری",
  "pros": ["کیفیت عالی"],
  "cons": ["گران‌قیمت"]
}
```

| فیلد | نوع | اجباری | قوانین |
|------|-----|--------|--------|
| `star` | integer | بله | ۱ تا ۵ |
| `text` | string | بله | min 10، max 2000 کاراکتر |
| `title` | string | خیر | max 300 کاراکتر |
| `pros` | `string[]` | خیر | آرایه نقاط مثبت |
| `cons` | `string[]` | خیر | آرایه نقاط منفی |

**Response `201`:**
```json
{
  "data": {
    "id": 101,
    "userName": "نام کاربر",
    "star": 4,
    "title": "عنوان اختیاری",
    "text": "متن نظر کاربر",
    "pros": ["کیفیت عالی"],
    "cons": ["گران‌قیمت"],
    "date": "۷ تیر ۱۴۰۵",
    "likes": 0,
    "dislikes": 0,
    "userVote": null,
    "images": []
  },
  "message": "نظر شما با موفقیت ثبت شد و پس از تأیید نمایش داده می‌شود."
}
```

**Response `400` (خطای اعتبارسنجی):**
```json
{
  "message": "خطا در اطلاعات ارسالی",
  "errors": {
    "star": "امتیاز الزامی است",
    "text": "متن نظر باید حداقل ۱۰ کاراکتر باشد"
  }
}
```

**Response `409` (نظر تکراری):**
```json
{
  "error": { "code": "CONFLICT", "message": "شما قبلاً برای این محصول نظر ثبت کرده‌اید" }
}
```

---

### POST `/api/v1/comments/{commentId}/helpful/`

رأی لایک یا دیسلایک روی یک نظر. ارسال دوباره همان رأی، آن را **حذف** می‌کند (toggle).

**Auth:** اجباری

**Request Body (`application/json`):**
```json
{ "type": "like" }
```

| فیلد | نوع | مقادیر مجاز |
|------|-----|------------|
| `type` | string | `"like"` \| `"dislike"` |

**Response `200`:**
```json
{
  "data": {
    "likes": 9,
    "dislikes": 2,
    "userVote": "like"
  }
}
```

> اگر کاربر رأی قبلی خود را toggle کند، `userVote` برابر `null` برمی‌گردد.

**Response `400`:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "مقدار type باید like یا dislike باشد",
    "field": "type"
  }
}
```

---

## پرسش‌ها (Questions)

### GET `/api/v1/products/{productId}/questions/`

لیست پرسش‌های یک محصول به همراه **تمام** پاسخ‌های هر پرسش.

**Auth:** اختیاری — اگر توکن ارسال شود `userVote` در پاسخ‌ها پر می‌شود.

**Query Parameters:**

| Param | Type | Default | مقادیر مجاز |
|-------|------|---------|------------|
| `sort` | string | `newest` | `newest` \| `most_answers` |
| `page` | integer | `1` | ≥ 1 |
| `limit` | integer | `10` | 1–100 |

**Response `200`:**
```json
{
  "data": {
    "totalCount": 42,
    "pagination": {
      "currentPage": 1,
      "totalPages": 5,
      "hasNext": true
    },
    "items": [
      {
        "id": 1,
        "text": "متن پرسش کاربر",
        "date": "۲۸ مهر ۱۴۰۳",
        "answerCount": 2,
        "answers": [
          {
            "id": 10,
            "userName": "کارشناس فروش",
            "date": "۲۹ مهر ۱۴۰۳",
            "text": "متن پاسخ",
            "likes": 5,
            "dislikes": 0,
            "userVote": null
          }
        ]
      }
    ]
  }
}
```

**نکات:**
- `answers`: شامل **تمام** پاسخ‌های هر پرسش است — pagination جداگانه‌ای برای پاسخ‌ها وجود ندارد.
- `answerCount`: تعداد کل پاسخ‌ها.
- صفحه‌بندی روی **پرسش‌ها** اعمال می‌شود، نه پاسخ‌ها.

---

### POST `/api/v1/products/{productId}/questions/`

ثبت پرسش جدید برای یک محصول.

**Auth:** اجباری

**Request Body (`application/json`):**
```json
{ "text": "متن پرسش کاربر" }
```

| فیلد | نوع | اجباری | قوانین |
|------|-----|--------|--------|
| `text` | string | بله | min 10، max 500 کاراکتر |

**Response `201`:**
```json
{
  "data": {
    "id": 50,
    "text": "متن پرسش کاربر",
    "date": "۷ تیر ۱۴۰۵",
    "answerCount": 0,
    "answers": []
  },
  "message": "پرسش شما با موفقیت ثبت شد."
}
```

**Response `400`:**
```json
{
  "message": "خطا در اطلاعات ارسالی",
  "errors": {
    "text": "این فیلد الزامی است."
  }
}
```

---

### POST `/api/v1/questions/{questionId}/answers/`

ثبت پاسخ به یک پرسش.

**Auth:** اجباری

**Request Body (`application/json`):**
```json
{ "text": "متن پاسخ" }
```

| فیلد | نوع | اجباری | قوانین |
|------|-----|--------|--------|
| `text` | string | بله | min 5، max 1000 کاراکتر |

**Response `201`:**
```json
{
  "data": {
    "id": 25,
    "userName": "نام کاربر",
    "date": "۷ تیر ۱۴۰۵",
    "text": "متن پاسخ",
    "likes": 0,
    "dislikes": 0,
    "userVote": null
  },
  "message": "پاسخ شما با موفقیت ثبت شد."
}
```

**Response `404`:**
```json
{
  "error": { "code": "NOT_FOUND", "message": "سوال یافت نشد" }
}
```

---

### POST `/api/v1/answers/{answerId}/helpful/`

رأی لایک یا دیسلایک روی یک پاسخ. ارسال دوباره همان رأی، آن را **حذف** می‌کند (toggle).

**Auth:** اجباری

**Request Body (`application/json`):**
```json
{ "type": "dislike" }
```

**Response `200`:**
```json
{
  "data": {
    "likes": 5,
    "dislikes": 1,
    "userVote": "dislike"
  }
}
```

---

## فرمت خطاها

دو نوع فرمت خطا در این API وجود دارد:

### ۱. خطای اعتبارسنجی فیلد — `400`
برای endpointهای POST که ورودی نامعتبر دریافت کنند:
```json
{
  "message": "خطا در اطلاعات ارسالی",
  "errors": {
    "field_name": "پیام خطای این فیلد"
  }
}
```

### ۲. خطای سیستمی — `401` / `404` / `409`
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "پیام خطا"
  }
}
```

| Status | Code | توضیح |
|--------|------|-------|
| `400` | — | خطای validation فیلد ورودی |
| `401` | — | توکن ارسال نشده یا منقضی شده |
| `404` | `NOT_FOUND` | محصول / نظر / پرسش / پاسخ یافت نشد |
| `409` | `CONFLICT` | نظر تکراری برای همین محصول |

---

## نکات یکپارچه‌سازی فرانت

**احراز هویت:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6...
```

**فرمت تاریخ:** همه تاریخ‌ها شمسی و فارسی هستند: `"۷ تیر ۱۴۰۵"`

**فیلد `userVote`:**
- کاربر لاگین‌نکرده → همیشه `null`
- کاربر لاگین‌کرده و رأی داده → `"like"` یا `"dislike"`
- کاربر لاگین‌کرده و رأی نداده → `null`

**Toggle رأی:** ارسال همان `type` قبلی، رأی را حذف می‌کند و `userVote: null` برمی‌گردد.

**صف تأیید نظرات:** نظر ثبت‌شده تا تأیید ادمین در لیست عمومی دیده **نمی‌شود**. `id` در response ثبت برمی‌گردد ولی در GET بعدی ظاهر نمی‌شود.