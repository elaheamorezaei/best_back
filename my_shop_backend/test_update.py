import requests

url = "http://127.0.0.1:8000/products/2/"

data = {
    "price": "6000000.00"
}

response = requests.patch(url, json=data)

print("وضعیت پاسخ:", response.status_code)
print("پاسخ سرور:")
print(response.json())
