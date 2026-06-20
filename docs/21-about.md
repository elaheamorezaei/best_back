# درباره ما (About)

**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** همه endpointها عمومی هستند (بدون احراز هویت).

> **فرمت پاسخ:** `{"success": true, "data": {...}}`

---

## 1. صفحه کامل درباره ما

```
GET /about/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "hero": {
      "title": "درباره بست",
      "subtitle": "پیشرو در فروش آنلاین لوازم خانگی",
      "description": "بست از سال ۱۳۹۵ با هدف...",
      "image": "http://localhost:8000/media/about/hero.jpg"
    },
    "stats": {
      "customers": 250000,
      "products": 5000,
      "brands": 150,
      "cities": 300
    },
    "story": {
      "title": "داستان ما",
      "content": "<p>بست در سال ۱۳۹۵...</p>",
      "image": "http://localhost:8000/media/about/story.jpg"
    },
    "team": [
      {
        "id": 1,
        "name": "محمد احمدی",
        "role": "مدیرعامل",
        "bio": "با ۱۵ سال سابقه در صنعت تجارت الکترونیک...",
        "avatar": "http://localhost:8000/media/about/team/ceo.jpg",
        "linkedin": "https://linkedin.com/in/..."
      }
    ],
    "values": [
      {
        "id": 1,
        "title": "اعتماد",
        "description": "ما به صداقت و شفافیت با مشتریان پایبندیم",
        "icon": "trust"
      },
      {
        "id": 2,
        "title": "کیفیت",
        "description": "فقط محصولات اصل و با کیفیت",
        "icon": "quality"
      }
    ],
    "awards": [
      {
        "id": 1,
        "title": "بهترین فروشگاه آنلاین",
        "year": "۱۴۰۲",
        "organization": "انجمن تجارت الکترونیک ایران",
        "image": "http://localhost:8000/media/about/awards/1.jpg"
      }
    ],
    "partners": [
      {
        "id": 1,
        "name": "امرسان",
        "logo": "http://localhost:8000/media/about/partners/emersun.png",
        "link": "https://emersun.com"
      }
    ]
  }
}
```

| فیلد | نوع | توضیح |
|------|-----|-------|
| `stats` | object | آمار کلی (تعداد مشتری، محصول، برند، شهر) |
| `team` | array | اعضای تیم — ممکن است خالی باشد |
| `values` | array | ارزش‌های شرکت |
| `awards` | array | جوایز دریافت‌شده |
| `partners` | array | برندهای همکار |

---

## 2. هرو درباره ما

```
GET /about/hero/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "title": "درباره بست",
    "subtitle": "پیشرو در فروش آنلاین لوازم خانگی",
    "description": "بست از سال ۱۳۹۵...",
    "image": "http://localhost:8000/media/about/hero.jpg"
  }
}
```

---

## 3. آمار

```
GET /about/stats/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "customers": 250000,
    "products": 5000,
    "brands": 150,
    "cities": 300
  }
}
```

---

## 4. داستان ما

```
GET /about/story/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "title": "داستان ما",
    "content": "<p>بست در سال ۱۳۹۵...</p>",
    "image": "http://localhost:8000/media/about/story.jpg"
  }
}
```

---

## 5. تیم

```
GET /about/team/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "members": [
      {
        "id": 1,
        "name": "محمد احمدی",
        "role": "مدیرعامل",
        "bio": "با ۱۵ سال سابقه...",
        "avatar": "http://localhost:8000/media/about/team/ceo.jpg",
        "linkedin": "https://linkedin.com/in/..."
      }
    ]
  }
}
```

---

## 6. ارزش‌ها

```
GET /about/values/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "values": [
      {
        "id": 1,
        "title": "اعتماد",
        "description": "ما به صداقت...",
        "icon": "trust"
      }
    ]
  }
}
```

---

## 7. جوایز

```
GET /about/awards/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "awards": [
      {
        "id": 1,
        "title": "بهترین فروشگاه آنلاین",
        "year": "۱۴۰۲",
        "organization": "انجمن تجارت الکترونیک ایران",
        "image": "http://localhost:8000/media/about/awards/1.jpg"
      }
    ]
  }
}
```

---

## 8. برندهای همکار

```
GET /about/partners/
```

### Response 200
```json
{
  "success": true,
  "data": {
    "partners": [
      {
        "id": 1,
        "name": "امرسان",
        "logo": "http://localhost:8000/media/about/partners/emersun.png",
        "link": "https://emersun.com"
      }
    ]
  }
}
```
