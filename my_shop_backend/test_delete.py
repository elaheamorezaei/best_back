import requests

# آیدی یکی از محصولات رو اینجا بزن (مثلاً محصولی که همین الان آپدیت کردی)
url = "http://127.0.0.1:8000/products/2/"

try:
    response = requests.delete(url)
    # وضعیت 204 در REST یعنی "با موفقیت حذف شد و محتوایی برای نمایش وجود ندارد"
    print("وضعیت پاسخ حذف:", response.status_code)
except Exception as e:
    print("خطا در حذف:", e)
