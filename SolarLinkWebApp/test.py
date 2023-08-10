import json
import requests

dict = {'username': 'ivan', "password": "1233"}
dict = {}
answer = requests.get("http://127.0.0.1:8000/user/load_data", dict)
print(answer.json())