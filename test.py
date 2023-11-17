import requests
import json

data ={ "username": "helyivan",
        "password": "12345678",
        "voltaje_hora_red" : 220,
        "consumo_hora_solar" : 300,
        "consumo_hora_red" : 500,
        "consumo_l1_solar" : 200,
        "consumo_l2_solar" : 302,
        "consumo_l1_proveedor" : 500,
        "consumo_l2_proveedor" : 250,
        "solar_ahora" : True }

var = requests.post("http://127.0.0.1:8000/user/load-data/", json=data)

print(var.json())