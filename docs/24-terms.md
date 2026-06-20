# قوانین و مقررات (Terms)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها عمومی هستند مگر `/terms/accept/` که نیاز به احراز هویت دارد.

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. لیست قوانین

```
GET /terms/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "terms": [
      {
        "id": 1,
        "question": "شرایط خرید از بست چیست؟",
        "answer": "کاربران باید حداقل ۱۸ سال سن داشته باشند...",
        "order": 1
      },
      {
        "id": 2,
        "question": "آیا می‌توانم کالا را برگشت دهم؟",
        "answer": "بله، در صورت رعایت شرایط، کالا تا ۷ روز قابل برگشت است...",
        "order": 2
      }
    ],
    "lastUpdated": "1403/12/01",
    "version": "2.1"
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `lastUpdated` | string | آخرین تاریخ بروزرسانی قوانین (جلالی) |
| `version` | string | نسخه فعلی قوانین |

---

## 2. جزئیات یک قانون

```
GET /terms/{term_id}/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "id": 1,
    "question": "شرایط خرید از بست چیست؟",
    "answer": "کاربران باید حداقل ۱۸ سال سن داشته باشند و اطلاعات صحیح ارائه دهند...",
    "order": 1,
    "lastUpdated": "1403/12/01"
  }
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "قانون یافت نشد"}` |

---

## 3. هرو صفحه قوانین

```
GET /terms/hero/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "title": "قوانین و مقررات",
    "subtitle": "لطفاً پیش از خرید این موارد را مطالعه فرمایید",
    "lastUpdated": "1403/12/01"
  }
}
```

---

## 4. شرایط استفاده از کیف پول

```
GET /terms/wallet/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "title": "شرایط و قوانین کیف پول بست",
    "sections": [
      {
        "id": 1,
        "title": "تعریف کیف پول",
        "content": "کیف پول بست یک ابزار پرداخت الکترونیکی است که..."
      },
      {
        "id": 2,
        "title": "شرایط شارژ",
        "content": "حداقل مبلغ شارژ ۱۰,۰۰۰ ریال است..."
      },
      {
        "id": 3,
        "title": "شرایط برداشت",
        "content": "برداشت از کیف پول تنها به حساب بانکی ثبت‌شده امکان‌پذیر است..."
      },
      {
        "id": 4,
        "title": "مسئولیت‌ها",
        "content": "در صورت سوء استفاده از کیف پول، بست مسئولیتی نخواهد داشت..."
      }
    ]
  }
}
```

---

## 5. پذیرش قوانین

```
POST /terms/accept/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "version": "2.1"
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `version` | ✅ | نسخه قوانینی که کاربر می‌پذیرد |

### Response 200
```json
{
  "success": true,
  "message": "قوانین با موفقیت پذیرفته شد",
  "data": {
    "acceptedVersion": "2.1",
    "acceptedAt": "1403/06/15 10:30"
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "نسخه قوانین نامعتبر است"}` |
