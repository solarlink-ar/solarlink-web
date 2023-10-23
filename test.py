import requests
import json
var = requests.post("https://solarlink.ar/user/api-login/", json={"username": "helyivan", "password": "12345678"})

print(var.json())