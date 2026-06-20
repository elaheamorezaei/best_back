# احراز هویت (Authentication)

**Base URL:** `http://localhost:8000/api/v1`  
**Content-Type:** `application/json`

---

## فرمت عمومی پاسخ‌ها

```json
// موفق
{ "success": true, "data": { ... } }

// خطا
{ "success": false, "message": "پیام خطا" }

// خطای اعتبارسنجی (422)
{ "success": false, "message": "خطای اعتبارسنجی", "errors": { "fieldName": "پیام" } }
```

---

## 1. بررسی شماره موبایل

```
POST /auth/phone/
```

### Request Body
```json
{
  "phoneNumber": "09121234567"
}
```

### Response 200
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

| فیلد | نوع | توضیح |
|------|-----|-------|
| `isRegistered` | boolean | آیا شماره قبلاً ثبت‌نام کرده |
| `nextStep` | string | `"password"` اگر ثبت‌نام کرده / `"otp"` اگر نکرده |
| `maskedPhone` | string | شماره با ماسک برای نمایش |

### Errors
| کد | توضیح |
|----|-------|
| `422` | `{"success": false, "message": "شماره موبایل نامعتبر است", "errors": {"phoneNumber": "..."}}` |

---

## 2. ورود با رمز عبور

```
POST /auth/login/password/
```

### Request Body
```json
{
  "phoneNumber": "09121234567",
  "password": "mypassword"
}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
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

### Errors
| کد | body |
|----|------|
| `401` | `{"success": false, "message": "رمز عبور اشتباه است", "code": "INVALID_PASSWORD"}` |
| `404` | `{"success": false, "message": "شماره موبایل یافت نشد"}` |
| `422` | `{"success": false, "message": "...", "errors": {...}}` |
| `429` | `{"success": false, "message": "X دقیقه دیگر تلاش کنید", "data": {"retryAfterSeconds": 300}}` |

---

## 3. ارسال کد OTP

```
POST /auth/otp/send/
```

### Request Body
```json
{
  "phoneNumber": "09121234567"
}
```

### Response 200
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

> `debugCode` فقط در محیط `DEBUG=True` وجود دارد

### Errors
| کد | body |
|----|------|
| `422` | `{"success": false, "message": "شماره موبایل نامعتبر است"}` |
| `429` | `{"success": false, "message": "هنوز X ثانیه باقی است", "data": {"retryAfterSeconds": 45}}` |

---

## 4. تأیید کد OTP (ورود یا ثبت‌نام)

```
POST /auth/otp/verify/
```

### Request Body
```json
{
  "phoneNumber": "09121234567",
  "code": "12345"
}
```

### Response 200
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

> `isNewUser: true` → کاربر تازه ثبت‌نام کرده (پروفایل را تکمیل کند)

### Errors
| کد | body |
|----|------|
| `410` | `{"success": false, "message": "کد تایید منقضی شده است", "code": "EXPIRED_OTP"}` |
| `422` | `{"success": false, "message": "کد تایید اشتباه است", "code": "INVALID_OTP"}` |

---

## 5. فراموشی رمز — ارسال OTP

```
POST /auth/forgot-password/send-otp/
```

### Request Body
```json
{
  "phoneNumber": "09121234567"
}
```

### Response 200
```json
{
  "success": true,
  "message": "کد تایید به شماره موبایل شما ارسال شد",
  "data": {
    "maskedPhone": "0912***4567",
    "expiresInSeconds": 120,
    "resetToken": "abc123def456abc123def456"
  }
}
```

> **مهم:** `resetToken` را نگه دارید — در مرحله بعد نیاز است

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "شماره موبایل در سیستم ثبت نشده است"}` |
| `429` | cooldown مانند OTP send |

---

## 6. فراموشی رمز — تأیید OTP

```
POST /auth/forgot-password/verify-otp/
```

### Request Body
```json
{
  "phoneNumber": "09121234567",
  "code": "12345",
  "resetToken": "abc123def456abc123def456"
}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "verified": true,
    "changeToken": "xyz789xyz789xyz789xyz789"
  }
}
```

> **مهم:** `changeToken` را نگه دارید — در مرحله بعد نیاز است

### Errors
| کد | body |
|----|------|
| `410` | `{"success": false, "message": "کد تایید منقضی شده است", "code": "EXPIRED_OTP"}` |
| `410` | `{"success": false, "message": "توکن منقضی شده", "code": "EXPIRED_RESET_TOKEN"}` |
| `422` | `{"success": false, "message": "کد اشتباه است", "code": "INVALID_OTP"}` |
| `422` | `{"success": false, "message": "توکن نامعتبر است", "code": "INVALID_RESET_TOKEN"}` |

---

## 7. فراموشی رمز — تغییر رمز

```
POST /auth/forgot-password/reset/
```

### Request Body
```json
{
  "changeToken": "xyz789xyz789xyz789xyz789",
  "newPassword": "NewPass@123",
  "confirmPassword": "NewPass@123"
}
```

### Response 200
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

### Errors
| کد | body |
|----|------|
| `410` | `{"success": false, "message": "توکن منقضی شده", "code": "EXPIRED_CHANGE_TOKEN"}` |
| `422` | `{"success": false, "message": "توکن نامعتبر است", "code": "INVALID_CHANGE_TOKEN"}` |
| `422` | `{"success": false, "message": "خطای اعتبارسنجی", "errors": {"newPassword": "..."}}` |

---

## 8. خروج (Logout)

```
POST /auth/logout/
Authorization: Bearer {accessToken}
```

### Request Body
```json
{
  "refreshToken": "eyJ..."
}
```

### Response 200
```json
{
  "success": true,
  "message": "با موفقیت خارج شدید"
}
```

---

## 9. تجدید توکن

```
POST /auth/refresh/
```

### Request Body
```json
{
  "refreshToken": "eyJ..."
}
```

### Response 200
```json
{
  "success": true,
  "data": {
    "accessToken": "eyJ...",
    "expiresIn": 3600
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "refreshToken الزامی است"}` |
| `401` | `{"success": false, "message": "توکن نامعتبر یا منقضی است", "code": "INVALID_TOKEN"}` |
