from machine import Pin, RTC
from solarlink import Solarlink
import time
import ujson as json
import urequests as requests
'''
#payload = json.dumps({"username": "helyivan", "password": "12345678"})
payload = json.dumps({"username": "helyivan", "password": "12345678", "voltaje_hora_red": 220,
                      "consumo_hora_solar": 400,
                      "consumo_hora_red": 400,
                      "consumo_l1_solar": 400,
                      "consumo_l1_proveedor": 400,
                      "consumo_l2_solar":400,
                      "consumo_l2_proveedor":400,
                      "hora": 20,
                      "dia": 24,
                      "mes": 10,
                      "agno": 2023,
                      "solar_ahora": True})
r = requests.post("http://192.168.0.18:8080/user/load-data/", data=payload)
print(r.text)
'''
rtc = RTC()
print(rtc.datetime())
