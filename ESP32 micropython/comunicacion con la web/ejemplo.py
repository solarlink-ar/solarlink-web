import network, json, time
import urequests as requests

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
while not wlan.isconnected():
    try:
        wlan.connect('Red Alumnos', '')
    except:
        pass
    

post_data = json.dumps({'data': '1234'})
requests.get('https://web-solarlink.ivancenyko.repl.co/datos', data = post_data)
