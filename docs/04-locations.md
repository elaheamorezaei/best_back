# استان‌ها و شهرها (Locations)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها عمومی هستند (بدون احراز هویت).

---

## 1. لیست استان‌ها

```
GET /locations/provinces/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "provinces": [
      { "id": 1, "name": "تهران" },
      { "id": 2, "name": "اصفهان" },
      { "id": 3, "name": "فارس" }
    ]
  }
}
```

---

## 2. شهرهای یک استان (path param)

```
GET /locations/provinces/{province_id}/cities/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "cities": [
      { "id": 1, "name": "تهران" },
      { "id": 2, "name": "شهریار" },
      { "id": 3, "name": "کرج" }
    ]
  }
}
```

### Errors
| کد | body |
|----|------|
| `404` | `{"success": false, "message": "استان یافت نشد"}` |

---

## 3. شهرهای یک استان (query param)

```
GET /locations/cities/?provinceId={id}
```

> همان پاسخ endpoint بالا را برمی‌گرداند.

### Query Parameters
| پارامتر | اجباری | توضیح |
|---------|--------|-------|
| `provinceId` | ✅ | شناسه استان |

### Response 200
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

### Errors
| کد | body |
|----|------|
| `400` | `{"success": false, "message": "پارامتر provinceId الزامی است"}` |
| `404` | `{"success": false, "message": "استان یافت نشد"}` |
