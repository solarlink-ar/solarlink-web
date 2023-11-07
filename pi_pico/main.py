from solarlink_post import Solarlink_post
import machine, time, json, math, ads1115, network
from machine import Pin, ADC, I2C, Timer, UART
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import urequests as requests
import asyncio
import ujson as json

solarlink = Solarlink_post()
uart1 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
hora_inicial = solarlink.rtc.datetime()[4]

async def post():
    global solarlink
    global hora_inicial 
    if hora_inicial != solarlink.rtc.datetime()[4]:
        uart1.write("hr")
        while not uart1.any():
            pass
        received_payload = uart1.read() 
        received_payload = json.loads(received_payload)
        solarlink.acumulador(received_payload)
        time = solarlink.rtc.datetime()
        payload = json.dumps({"username": solarlink.username, "password": solarlink.password,
                "voltaje_hora_red": solarlink.acumulacion_voltaje_red / solarlink.indice_mediciones,
                "consumo_hora_solar": solarlink.acumulacion_consumo_solar / solarlink.indice_mediciones,
                "consumo_hora_red": solarlink.acumulacion_consumo_red / solarlink.indice_mediciones,
                "consumo_l1_solar": solarlink.acumulacion_consumo_l1_solar / solarlink.indice_mediciones,
                "consumo_l1_proveedor": solarlink.acumulacion_consumo_l1_proveedor / solarlink.indice_mediciones,
                "consumo_l2_solar": solarlink.acumulacion_consumo_l2_solar / solarlink.indice_mediciones,
                "consumo_l2_proveedor": solarlink.acumulacion_consumo_l2_proveedor / solarlink.indice_mediciones,
                "hora": time[4],
                "dia": time[2],
                "mes": time[1],
                "agno": time[0],
                "solar_ahora": (solarlink.l1 or solarlink.l2)})
        
        solarlink.acumulacion_consumo_l1_proveedor = 0
        solarlink.acumulacion_consumo_l1_solar = 0
        solarlink.acumulacion_consumo_l2_proveedor = 0
        solarlink.acumulacion_consumo_l2_solar = 0
        solarlink.acumulacion_consumo_red = 0
        solarlink.acumulacion_consumo_solar = 0
        solarlink.acumulacion_voltaje_red = 0
        solarlink.indice_mediciones = 0

        hora_inicial = time[4]

        r = requests.post("http://10.0.2.104:8080/user/load-data/", data=payload)
        print(r.text)


async def tiempo_real():
    global solarlink
    solarlink.timer0 = Timer(0).init(period=1000, mode=Timer.ONE_SHOT, callback=solarlink.callback_posteo)
    if solarlink.tiempo_real:
        login_payload = json.dumps({"username": solarlink.username, "password": solarlink.password})
        r = requests.get("http://10.0.2.104:8080/user/user-is-online/", data=login_payload)

        response = json.loads(r.text)
        
        if response["response"]:
            uart1.write("nw")
            while not uart1.any():
                pass
            payload = uart1.read() 
            requests.post("http://10.0.2.104:8080/user/tiempo-real/", data = payload)
            
        solarlink.tiempo_real = False

        
async def main():
    #asyncio.create_task(mediciones())
    #asyncio.create_task(display())
    #asyncio.create_task(conmutacion())
    asyncio.create_task(post())
    asyncio.create_task(tiempo_real())


while 1:
    asyncio.run(main())



