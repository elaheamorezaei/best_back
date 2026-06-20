# علاقه‌مندی‌ها (Favorites / Wishlist)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها نیاز به `Authorization: Bearer {accessToken}` دارند.

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. لیست علاقه‌مندی‌ها

```
GET /favorites/
Authorization: Bearer {accessToken}
```

### Query Parameters
| پارامتر | نوع | پیش‌فرض |
|---------|-----|---------|
| `page` | number | `1` |
| `limit` | number | `12` |

### Response 200
```json
{
  "success": true,
  "data": {
    "pagination": {
      "currentPage": 1,
      "totalPages": 2,
      "totalCount": 18,
      "hasNext": true
    },
    "items": [
      {
        "id": 1,
        "productId": 10,
        "productName": "یخچال فریزر امرسان",
        "productImage": "http://localhost:8000/media/products/pic.jpg",
        "model": "N-lITE 203",
        "star": 4.3,
        "price": 2600000,
        "off": 20,
        "finalPrice": 2080000,
        "inStock": true,
        "addedAt": "1403/05/15"
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `id` | number | شناسه آیتم علاقه‌مندی |
| `productId` | number | شناسه محصول |
| `inStock` | boolean | آیا محصول موجود است |
| `addedAt` | string | تاریخ افزوده‌شدن به علاقه‌مندی (جلالی) |

---

## 2. افزودن محصول به علاقه‌مندی

```
POST /favorites/
Authorization: Bearer {accessToken}
Content-Type: application/json
```

### Request Body
```json
{
  "productId": 10
}
```

| فیلد | اجباری | توضیح |
|------|--------|-------|
| `productId` | ✅ | شناسه محصول |

### Response 201
```json
{
  "success": true,
  "message": "محصول به علاقه‌مندی‌ها اضافه شد",
  "data": {
    "id": 5,
    "productId": 10,
    "addedAt": "1403/06/15"
  }
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "محصول یافت نشد"}` |
| `409` | `{"success": false, "message": "این محصول از قبل در علاقه‌مندی‌های شما موجود است"}` |

---

## 3. حذف از علاقه‌مندی

```
DELETE /favorites/{product_id}/
Authorization: Bearer {accessToken}
```

> `product_id` در اینجا شناسه **محصول** است (نه شناسه آیتم علاقه‌مندی).

### Response 200
```json
{
  "success": true,
  "message": "محصول از علاقه‌مندی‌ها حذف شد"
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "محصول در علاقه‌مندی‌های شما یافت نشد"}` |
