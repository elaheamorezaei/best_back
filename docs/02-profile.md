# پروفایل کاربر (Profile)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها نیاز به `Authorization: Bearer {accessToken}` دارند.

---

## 1. دریافت اطلاعات پروفایل

```
GET /profile/
Authorization: Bearer {accessToken}
```

### Response 200
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

| فیلد | نوع | توضیح |
|------|-----|-------|
| `gender` | string | `"آقا"` \| `"خانم"` \| `""` |
| `birthDate` | string | تاریخ تولد جلالی — مثال: `"1370/05/15"` |
| `nationalCode` | string | کد ملی — ممکن است خالی باشد |
| `address` | string | آدرس متنی — ممکن است خالی باشد |
| `avatar` | string\|null | URL کامل تصویر یا `null` |
| `createdAt` | string | تاریخ ثبت‌نام جلالی |

---

## 2. ویرایش پروفایل

```
PUT /profile/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body (همه فیلدها اختیاری)
```json
{
  "fullName": "علی محمدی",
  "email": "ali@example.com",
  "gender": "آقا",
  "birthDate": "1370/5/15",
  "address": "تهران، خیابان ولیعصر، پلاک ۱۰"
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `fullName` | string | نام کامل |
| `email` | string | ایمیل معتبر |
| `gender` | string | `"آقا"` یا `"خانم"` |
| `birthDate` | string | فرمت: `YYYY/M/D` — مثال: `"1370/5/15"` |
| `address` | string | آدرس متنی |

### Response 200
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
    "address": "تهران، خیابان ولیعصر، پلاک ۱۰"
  }
}
```

### Errors
| کد | body |
|----|------|
| `422` | `{"success": false, "message": "خطای اعتبارسنجی", "errors": {"birthDate": "فرمت باید YYYY/M/D باشد"}}` |

---

## 3. آپلود آواتار

```
POST /profile/avatar/
Authorization: Bearer {accessToken}
Content-Type: multipart/form-data
```

### Request (form-data)
| فیلد | نوع | توضیح |
|------|-----|-------|
| `avatar` | file | **اجباری** — فرمت: JPG، PNG، WEBP — حداکثر ۲ مگابایت |

### Response 200
```json
{
  "success": true,
  "data": {
    "avatarUrl": "http://localhost:8000/media/avatars/pic.jpg"
  }
}
```

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "فایل آواتار الزامی است"}` |
| `400` | `{"success": false, "message": "حجم فایل نباید بیشتر از ۲ مگابایت باشد"}` |
| `400` | `{"success": false, "message": "فرمت فایل باید JPG، PNG یا WEBP باشد"}` |

---

## 4. تغییر رمز عبور

```
PUT /profile/password/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "currentPassword": "OldPass@123",
  "newPassword": "NewPass@456",
  "confirmPassword": "NewPass@456"
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `currentPassword` | ✅ | رمز عبور فعلی |
| `newPassword` | ✅ | رمز جدید — حداقل ۸ کاراکتر |
| `confirmPassword` | ✅ | باید با `newPassword` یکسان باشد |

### Response 200
```json
{
  "success": true,
  "message": "رمز عبور با موفقیت تغییر یافت"
}
```

### Errors
| کد | body |
|----|------|
| `401` | `{"success": false, "message": "رمز عبور فعلی اشتباه است", "code": "WRONG_CURRENT_PASSWORD"}` |
| `422` | `{"success": false, "message": "خطای اعتبارسنجی", "errors": {"confirmPassword": "رمزها یکسان نیستند"}}` |
