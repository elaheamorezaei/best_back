# نظرات و سوالات (Reviews & Questions)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** GET عمومی است — POST/vote نیاز به `Authorization: Bearer {accessToken}` دارد.

> **فرمت پاسخ:** `{"data": {...}}` (بدون `success`)

---

## 1. لیست نظرات محصول

```
GET /products/{product_id}/comments/
```

### Query Parameters
| پارامتر | نوع | مقادیر | پیش‌فرض |
|---------|-----|--------|---------|
| `sort` | string | `newest` \| `top_rated` \| `has_image` | `newest` |
| `page` | number | — | `1` |
| `limit` | number | حداکثر ۱۰۰ | `10` |

### Response 200
```json
{
  "data": {
    "summary": {
      "averageRating": 4.2,
      "totalCount": 28,
      "distribution": {
        "5": 12,
        "4": 8,
        "3": 5,
        "2": 2,
        "1": 1
      }
    },
    "pagination": {
      "currentPage": 1,
      "totalPages": 3,
      "hasNext": true,
      "totalCount": 28
    },
    "items": [
      {
        "id": 1,
        "userName": "علی محمدی",
        "star": 5,
        "text": "محصول عالی است، خیلی راضی هستم...",
        "date": "1403/05/20",
        "likes": 8,
        "dislikes": 1,
        "userVote": null,
        "images": [
          "http://localhost:8000/media/comments/1.jpg"
        ]
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `star` | number | ۱ تا ۵ |
| `userVote` | string\|null | `"like"` \| `"dislike"` \| `null` — فقط برای کاربران لاگین‌شده |
| `images` | array | لیست URL تصاویر ضمیمه نظر |

### Errors
| کد | body |
|----|------|
| `404` | `{"error": {"code": "NOT_FOUND", "message": "محصول یافت نشد"}}` |

---

## 2. ثبت نظر جدید

```
POST /products/{product_id}/comments/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "star": 5,
  "text": "این محصول واقعاً عالی است و کاملاً به توضیحات مطابقت دارد."
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `star` | ✅ | عدد ۱ تا ۵ |
| `text` | ✅ | حداقل ۱۰ کاراکتر — حداکثر ۲۰۰۰ کاراکتر |

### Response 201
```json
{
  "data": {
    "id": 5,
    "userName": "علی محمدی",
    "star": 5,
    "text": "این محصول واقعاً عالی است...",
    "date": "1403/06/15",
    "likes": 0,
    "dislikes": 0,
    "userVote": null,
    "images": []
  },
  "message": "نظر شما با موفقیت ثبت شد"
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"error": {"code": "VALIDATION_ERROR", "message": "متن نظر باید حداقل ۱۰ کاراکتر باشد", "field": "text"}}` |
| `404` | `{"error": {"code": "NOT_FOUND", "message": "محصول یافت نشد"}}` |
| `409` | `{"error": {"code": "CONFLICT", "message": "شما قبلاً برای این محصول نظر ثبت کرده‌اید"}}` |

---

## 3. مفید بودن نظر (Vote)

```
POST /comments/{comment_id}/helpful/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "type": "like"
}
```

| فیلد | مقادیر | توضیح |
|------|--------|-------|
| `type` | `"like"` \| `"dislike"` | نوع رای — اگر همان رای قبلاً ثبت شده بود، حذف می‌شود (toggle) |

### Response 200
```json
{
  "data": {
    "likes": 9,
    "dislikes": 1,
    "userVote": "like"
  }
}
```

> اگر رای حذف شود: `"userVote": null`

### Errors
| کد | body |
|----|------|
| `400` | `{"error": {"code": "VALIDATION_ERROR", "message": "مقدار type باید like یا dislike باشد", "field": "type"}}` |
| `404` | `{"error": {"code": "NOT_FOUND", "message": "نظر یافت نشد"}}` |

---

## 4. لیست سوالات محصول

```
GET /products/{product_id}/questions/
```

### Query Parameters
| پارامتر | نوع | مقادیر | پیش‌فرض |
|---------|-----|--------|---------|
| `sort` | string | `newest` \| `most_answers` | `newest` |
| `page` | number | — | `1` |
| `limit` | number | حداکثر ۱۰۰ | `10` |

### Response 200
```json
{
  "data": {
    "totalCount": 15,
    "pagination": {
      "currentPage": 1,
      "totalPages": 2,
      "hasNext": true
    },
    "items": [
      {
        "id": 1,
        "text": "آیا این یخچال نوفراست دارد؟",
        "date": "1403/05/10",
        "answerCount": 2,
        "answers": [
          {
            "id": 1,
            "userName": "پشتیبانی بست",
            "date": "1403/05/11",
            "text": "بله، این مدل دارای سیستم نوفراست است.",
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

> `answers` فقط ۲ پاسخ اول را نشان می‌دهد.

### Errors
| کد | body |
|----|------|
| `404` | `{"error": {"code": "NOT_FOUND", "message": "محصول یافت نشد"}}` |

---

## 5. ثبت سوال جدید

```
POST /products/{product_id}/questions/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "text": "آیا این یخچال نوفراست دارد و مصرف برقش چقدر است؟"
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `text` | ✅ | حداقل ۱۰ کاراکتر — حداکثر ۵۰۰ کاراکتر |

### Response 201
```json
{
  "data": {
    "id": 10,
    "text": "آیا این یخچال نوفراست دارد...",
    "date": "1403/06/15",
    "answerCount": 0,
    "answers": []
  },
  "message": "سوال شما با موفقیت ثبت شد"
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"error": {"code": "VALIDATION_ERROR", "message": "...", "field": "text"}}` |
| `404` | `{"error": {"code": "NOT_FOUND", "message": "محصول یافت نشد"}}` |

---

## 6. ثبت پاسخ برای سوال

```
POST /questions/{question_id}/answers/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "text": "بله، این مدل دارای سیستم نوفراست کامل است و مصرف برق کلاس +B دارد."
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `text` | ✅ | حداقل ۵ کاراکتر — حداکثر ۱۰۰۰ کاراکتر |

### Response 201
```json
{
  "data": {
    "id": 5,
    "userName": "علی محمدی",
    "date": "1403/06/15",
    "text": "بله، این مدل دارای سیستم نوفراست...",
    "likes": 0,
    "dislikes": 0,
    "userVote": null
  },
  "message": "پاسخ شما با موفقیت ثبت شد"
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"error": {"code": "NOT_FOUND", "message": "سوال یافت نشد"}}` |

---

## 7. مفید بودن پاسخ (Vote)

```
POST /answers/{answer_id}/helpful/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{ "type": "like" }
```

### Response 200
```json
{
  "data": {
    "likes": 6,
    "dislikes": 0,
    "userVote": "like"
  }
}
```
