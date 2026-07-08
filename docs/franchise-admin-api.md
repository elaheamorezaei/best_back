# API Documentation — مدیریت درخواست‌های نمایندگی (Admin)

> Base URL: `/api/v1`
> Content-Type: `application/json`
> تمام این endpointها نیاز به احراز هویت ادمین دارند.

---

## احراز هویت

همه درخواست‌ها باید هدر زیر را داشته باشند:

```http
Authorization: Bearer <access_token>
```

کاربر باید `is_staff = true` باشد، در غیر این صورت پاسخ `403 Forbidden` برمی‌گردد.

---

## مدل وضعیت درخواست

| مقدار      | برچسب نمایشی      |
| ---------- | ----------------- |
| `pending`  | در انتظار بررسی   |
| `approved` | تایید شده         |
| `rejected` | رد شده            |

---

## Endpoints

---

### 1. لیست درخواست‌های نمایندگی

```http
GET /api/v1/admin/franchise/
```

#### Query Parameters

| پارامتر    | نوع      | توضیح                                              |
| ---------- | -------- | -------------------------------------------------- |
| `status`   | `string` | فیلتر وضعیت: `pending` \| `approved` \| `rejected` |
| `search`   | `string` | جستجو در نام، شماره تماس، کد پیگیری               |
| `province` | `string` | فیلتر بر اساس استان                                |
| `page`     | `number` | شماره صفحه (پیش‌فرض: `1`)                          |
| `pageSize` | `number` | تعداد در هر صفحه (پیش‌فرض: `20`، حداکثر: `100`)   |

#### Response — `200 OK`

```json
{
  "results": [
    {
      "id": 1,
      "trackingCode": "FRN-2025-00001",
      "fullName": "علی محمدی",
      "phone": "09123456789",
      "email": "ali@example.com",
      "city": "اصفهان",
      "province": "اصفهان",
      "franchiseType": "store",
      "investmentRange": "50m_150m",
      "hasSalesExperience": true,
      "description": "توضیحات متقاضی",
      "status": "pending",
      "adminNote": "",
      "reviewedAt": null,
      "createdAt": "2025-07-01T14:22:00.000000+00:00"
    }
  ],
  "count": 42,
  "page": 1,
  "pageSize": 20,
  "totalPages": 3
}
```

---

### 2. جزئیات یک درخواست

```http
GET /api/v1/admin/franchise/{id}/
```

#### Response — `200 OK`

```json
{
  "id": 1,
  "trackingCode": "FRN-2025-00001",
  "fullName": "علی محمدی",
  "phone": "09123456789",
  "email": "ali@example.com",
  "city": "اصفهان",
  "province": "اصفهان",
  "franchiseType": "store",
  "investmentRange": "50m_150m",
  "hasSalesExperience": true,
  "description": "توضیحات متقاضی",
  "status": "pending",
  "adminNote": "",
  "reviewedAt": null,
  "createdAt": "2025-07-01T14:22:00.000000+00:00"
}
```

#### Response — `404 Not Found`

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "درخواست یافت نشد"
  }
}
```

---

### 3. ویرایش یادداشت ادمین

```http
PATCH /api/v1/admin/franchise/{id}/
```

#### Request Body

```json
{
  "adminNote": "متقاضی با شرایط موافق است، منتظر مدارک"
}
```

| فیلد        | نوع      | اجباری | توضیح              |
| ----------- | -------- | :----: | ------------------ |
| `adminNote` | `string` |   ✅   | یادداشت داخلی ادمین |

#### Response — `200 OK`

آبجکت کامل درخواست با `adminNote` آپدیت‌شده برمی‌گردد (همان فرمت جزئیات).

---

### 4. تایید درخواست

```http
POST /api/v1/admin/franchise/{id}/approve/
```

#### Request Body

```json
{
  "adminNote": "تایید شد — قرارداد ارسال می‌شود"
}
```

| فیلد        | نوع      | اجباری | توضیح                          |
| ----------- | -------- | :----: | ------------------------------ |
| `adminNote` | `string` |   ❌   | یادداشت اختیاری هنگام تایید    |

#### Response — `200 OK`

```json
{
  "success": true,
  "message": "درخواست نمایندگی تایید شد",
  "data": {
    "id": 1,
    "trackingCode": "FRN-2025-00001",
    "fullName": "علی محمدی",
    "phone": "09123456789",
    "email": "ali@example.com",
    "city": "اصفهان",
    "province": "اصفهان",
    "franchiseType": "store",
    "investmentRange": "50m_150m",
    "hasSalesExperience": true,
    "description": "توضیحات متقاضی",
    "status": "approved",
    "adminNote": "تایید شد — قرارداد ارسال می‌شود",
    "reviewedAt": "2025-07-08T10:05:00.000000+00:00",
    "createdAt": "2025-07-01T14:22:00.000000+00:00"
  }
}
```

#### Response — `404 Not Found`

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "درخواست یافت نشد"
  }
}
```

---

### 5. رد درخواست

```http
POST /api/v1/admin/franchise/{id}/reject/
```

#### Request Body

```json
{
  "adminNote": "سرمایه کافی نیست"
}
```

| فیلد        | نوع      | اجباری | توضیح                       |
| ----------- | -------- | :----: | --------------------------- |
| `adminNote` | `string` |   ❌   | یادداشت اختیاری هنگام رد    |

#### Response — `200 OK`

```json
{
  "success": true,
  "message": "درخواست نمایندگی رد شد",
  "data": {
    "id": 1,
    "trackingCode": "FRN-2025-00001",
    "status": "rejected",
    "adminNote": "سرمایه کافی نیست",
    "reviewedAt": "2025-07-08T10:10:00.000000+00:00",
    "createdAt": "2025-07-01T14:22:00.000000+00:00"
  }
}
```

---

### 6. حذف درخواست

```http
DELETE /api/v1/admin/franchise/{id}/
```

#### Response — `204 No Content`

بدون body.

#### Response — `404 Not Found`

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "درخواست یافت نشد"
  }
}
```

---

## مقادیر مجاز فیلدها

### `franchiseType`

| مقدار    | برچسب نمایشی            |
| -------- | ----------------------- |
| `store`  | فروشگاهی (حضوری)        |
| `online` | اینترنتی (آنلاین)       |
| `hybrid` | ترکیبی (حضوری + آنلاین) |

### `investmentRange`

| مقدار        | برچسب نمایشی             |
| ------------ | ------------------------ |
| `under_50m`  | کمتر از ۵۰ میلیون تومان  |
| `50m_150m`   | ۵۰ تا ۱۵۰ میلیون تومان  |
| `150m_300m`  | ۱۵۰ تا ۳۰۰ میلیون تومان |
| `above_300m` | بیش از ۳۰۰ میلیون تومان |

---

## خلاصه Endpoints

| Method   | URL                                      | توضیح                    |
| -------- | ---------------------------------------- | ------------------------ |
| `GET`    | `/api/v1/admin/franchise/`               | لیست + فیلتر + صفحه‌بندی |
| `GET`    | `/api/v1/admin/franchise/{id}/`          | جزئیات یک درخواست        |
| `PATCH`  | `/api/v1/admin/franchise/{id}/`          | ویرایش یادداشت ادمین     |
| `DELETE` | `/api/v1/admin/franchise/{id}/`          | حذف درخواست              |
| `POST`   | `/api/v1/admin/franchise/{id}/approve/`  | تایید درخواست            |
| `POST`   | `/api/v1/admin/franchise/{id}/reject/`   | رد درخواست               |
