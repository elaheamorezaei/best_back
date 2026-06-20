import requests

url = "http://127.0.0.1:8000/api/token/"
data = {
    "username": "your_username",
    "password": "your_password"
}

response = requests.post(url, data=data)
print(response.status_code)
print(response.json())
