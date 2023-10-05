import requests

data = requests.post("http://127.0.0.1:8000/user/api-login/", {"username": "helyivan", "password": "12345678"})
print(data.json())