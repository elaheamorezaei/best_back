# سوالات متداول (FAQ)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها عمومی هستند مگر ارسال سوال.

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. دسته‌بندی‌های FAQ

```
GET /faq/categories/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": 1,
        "name": "خرید و پرداخت",
        "slug": "purchase",
        "icon": "shopping-cart",
        "questionCount": 12
      },
      {
        "id": 2,
        "name": "ارسال و تحویل",
        "slug": "delivery",
        "icon": "truck",
        "questionCount": 8
      },
      {
        "id": 3,
        "name": "بازگشت کالا",
        "slug": "return",
        "icon": "refresh",
        "questionCount": 6
      }
    ]
  }
}
```

---

## 2. لیست سوالات FAQ

```
GET /faq/
```

### Query Parameters
| پارامتر | نوع | توضیح |
|---------|-----|-------|
| `category` | number | فیلتر بر اساس ID دسته‌بندی |
| `page` | number | پیش‌فرض `1` |
| `limit` | number | پیش‌فرض `20` |

### Response 200
```json
{
  "success": true,
  "data": {
    "pagination": {
      "currentPage": 1,
      "totalPages": 2,
      "totalCount": 26,
      "hasNext": true
    },
    "items": [
      {
        "id": 1,
        "question": "چگونه می‌توانم سفارشم را پیگیری کنم؟",
        "answer": "پس از ارسال سفارش، کد رهگیری از طریق پیامک ارسال می‌شود...",
        "category": {
          "id": 2,
          "name": "ارسال و تحویل"
        },
        "helpfulCount": 45,
        "notHelpfulCount": 3,
        "isPopular": true
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `helpfulCount` | number | تعداد رای «مفید بود» |
| `notHelpfulCount` | number | تعداد رای «مفید نبود» |
| `isPopular` | boolean | آیا سوال پرطرفدار است |

---

## 3. جستجو در FAQ

```
GET /faq/search/?q={query}
```

### Query Parameters
| پارامتر | اجباری | توضیح |
|---------|--------|-------|
| `q` | ✅ | عبارت جستجو — حداقل ۳ کاراکتر |

### Response 200
```json
{
  "success": true,
  "data": {
    "query": "پیگیری سفارش",
    "totalCount": 3,
    "items": [
      {
        "id": 1,
        "question": "چگونه می‌توانم سفارشم را پیگیری کنم؟",
        "answer": "پس از ارسال سفارش...",
        "category": {
          "id": 2,
          "name": "ارسال و تحویل"
        },
        "helpfulCount": 45
      }
    ]
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "حداقل ۳ کاراکتر وارد کنید"}` |

---

## 4. جزئیات یک سوال FAQ

```
GET /faq/{faq_id}/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "id": 1,
    "question": "چگونه می‌توانم سفارشم را پیگیری کنم؟",
    "answer": "پس از ارسال سفارش، کد رهگیری از طریق پیامک ارسال می‌شود. شما می‌توانید از طریق بخش پروفایل > سفارش‌های من > ردیابی سفارش، وضعیت ارسال را مشاهده کنید.",
    "category": {
      "id": 2,
      "name": "ارسال و تحویل",
      "slug": "delivery"
    },
    "helpfulCount": 45,
    "notHelpfulCount": 3,
    "isPopular": true,
    "relatedFaqs": [
      {
        "id": 3,
        "question": "مدت زمان تحویل سفارش چقدر است؟"
      }
    ]
  }
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "سوال یافت نشد"}` |

---

## 5. رای به FAQ (مفید / غیرمفید)

```
POST /faq/{faq_id}/helpful/
Content-Type: application/json
```

> این endpoint عمومی است (بدون احراز هویت).

### Request Body
```json
{
  "type": "helpful"
}
```

| فیلد | مقادیر | توضیح |
|------|--------|-------|
| `type` | `"helpful"` \| `"not_helpful"` | نوع رای |

### Response 200
```json
{
  "success": true,
  "data": {
    "helpfulCount": 46,
    "notHelpfulCount": 3
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "مقدار type نامعتبر است"}` |
| `404` | `{"success": false, "message": "سوال یافت نشد"}` |

---

## 6. ارسال سوال جدید

```
POST /faq/ask/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "question": "آیا امکان پرداخت اقساطی وجود دارد؟",
  "categoryId": 1,
  "email": "ali@example.com"
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `question` | ✅ | متن سوال — حداقل ۱۰ کاراکتر |
| `categoryId` | ❌ | شناسه دسته‌بندی |
| `email` | ❌ | ایمیل برای دریافت پاسخ |

### Response 201
```json
{
  "success": true,
  "message": "سوال شما با موفقیت ثبت شد. پس از بررسی پاسخ داده خواهد شد.",
  "data": {
    "id": "ASK-1403-00056",
    "question": "آیا امکان پرداخت اقساطی وجود دارد؟",
    "submittedAt": "1403/06/15"
  }
}
```

### Errors
| کد | body |
|----|------|
| `422` | `{"success": false, "errors": {"question": "متن سوال باید حداقل ۱۰ کاراکتر باشد"}}` |
