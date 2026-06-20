import requests
import json

    # آدرس API که محصول رو بهش ارسال می‌کنیم
url = "http://127.0.0.1:8000/products/"

    # اطلاعات محصول جدیدی که می‌خوایم بسازیم
    # توجه: آیدی دسته‌بندی (category) باید موجود باشه!
    # فرض می‌کنیم آیدی 1 برای دسته‌بندی "لوازم خانگی" باشه
new_product_data = {
        "name": "جاروبرقی رباتیک",
        "category": 1,  # آیدی دسته‌بندی مورد نظر
        "price": 5500000,
        "stock": 50,
        "description": "جاروبرقی هوشمند با قابلیت نقشه برداری"
    }

    # ارسال درخواست POST
try:
        response = requests.post(
            url,
            data=json.dumps(new_product_data),
            headers={'Content-Type': 'application/json'}
        )

        # بررسی نتیجه
        if response.status_code == 201: # 201 یعنی موفقیت آمیز ساخته شد
            print("محصول با موفقیت ساخته شد!")
            print("پاسخ سرور:")
            print(response.json())
        else:
            print(f"خطا در ساخت محصول. کد خطا: {response.status_code}")
            print("پاسخ سرور:")
            print(response.json()) # اطلاعات خطا رو نشون میده

except requests.exceptions.ConnectionError:
        print("خطا: سرور در حال اجرا نیست یا آدرس اشتباه است.")
except Exception as e:
        print(f"یک خطای پیش‌بینی نشده رخ داد: {e}")