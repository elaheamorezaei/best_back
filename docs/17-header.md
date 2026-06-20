# هدر و منوی اصلی (Header / Mega Menu)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** عمومی (بدون احراز هویت).

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. مگامنو

```
GET /header/mega-menu/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": 1,
        "name": "یخچال و فریزر",
        "slug": "refrigerator",
        "icon": "fridge",
        "image": "http://localhost:8000/media/categories/fridge.jpg",
        "link": "/category/refrigerator",
        "subcategories": [
          {
            "id": 10,
            "name": "یخچال فریزر دو درب",
            "slug": "double-door",
            "link": "/category/double-door"
          },
          {
            "id": 11,
            "name": "یخچال ایستاده",
            "slug": "standing",
            "link": "/category/standing"
          }
        ],
        "featuredBrands": [
          {
            "id": 1,
            "name": "امرسان",
            "logo": "http://localhost:8000/media/brands/emersun.png"
          },
          {
            "id": 2,
            "name": "الجی",
            "logo": "http://localhost:8000/media/brands/lg.png"
          }
        ],
        "bannerImage": "http://localhost:8000/media/menu-banners/fridge-banner.jpg",
        "bannerLink": "/offers/refrigerators"
      },
      {
        "id": 2,
        "name": "ماشین لباسشویی",
        "slug": "washing-machine",
        "icon": "washer",
        "image": "http://localhost:8000/media/categories/washer.jpg",
        "link": "/category/washing-machine",
        "subcategories": [],
        "featuredBrands": [],
        "bannerImage": null,
        "bannerLink": null
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `icon` | string | نام آیکون برای نمایش در منو |
| `subcategories` | array | دسته‌بندی‌های فرزند — ممکن است خالی باشد |
| `featuredBrands` | array | برندهای برجسته این دسته — ممکن است خالی باشد |
| `bannerImage` | string\|null | بنر تبلیغاتی در منو — اگر ندارد `null` |
| `bannerLink` | string\|null | لینک بنر — اگر `bannerImage` ندارد `null` |
