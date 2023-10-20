#import urequests as requests
import requests

pete = requests.post("https://solarlink.ar/user/api-login", {"username": "helyivan"}, {"password": "12345678"})

print(pete)
