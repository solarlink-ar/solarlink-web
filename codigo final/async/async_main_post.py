from solarlink import Solarlink
import machine, time, json, math, ads1115, network
from machine import Pin, ADC, I2C, Timer, UART
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import urequests as requests
import uasyncio as asyncio
import ujson as json

solarlink = Solarlink()

async def mediciones():
    global solarlink
    solarlink.medicion_default_segundo()

async def display():
    global solarlink
    valores = solarlink.medicion
    solarlink.lcd.hal_write_command(LcdApi.LCD_HOME)
    solarlink.lcd.hide_cursor()

    sol = bytearray([0x00,0x00,0x15,0x0E,0x1B,0x0E,0x15,0x00])
    solarlink.lcd.custom_char(0, sol)
    if solarlink.l1:
        sol_l1 = chr(0)
    else:
        sol_l1 = ' '
    if solarlink.l2:
        sol_l2 = chr(0)
    else:
        sol_l2 = ' '
    solarlink.lcd.move_to(0,0)
    solarlink.lcd.putstr(f"{sol_l1}" + "    " + f"Vin:{valores['voltaje']} V" + "     " + f"{sol_l2}")
    solarlink.lcd.move_to(0,1)
    solarlink.lcd.putstr(f"LINEA1        LINEA2")
    solarlink.lcd.move_to(0,2)
    solarlink.lcd.putstr(f"%.2f A"% (valores["corriente_l1"]) + "        " + "%.2f A" % (valores["corriente_l2"]))
    solarlink.lcd.move_to(0,3)
    solarlink.lcd.putstr('{:0>4d} W'.format(valores["consumo_l1"]) + "        " + '{:0>4d} W'.format(valores["consumo_l2"]))


async def conmutacion():
    global solarlink
    trigger = solarlink.trigger
    consumo_l1 = solarlink.medicion["consumo_l1"]
    consumo_l2 = solarlink.medicion["consumo_l2"]

    # logica de conmutacion
    if consumo_l1 + consumo_l2 < trigger:
        solarlink.conmutador(l1 = True, l2 = True)
    else:
        if consumo_l1 < trigger and consumo_l2 < trigger:
            if consumo_l1 > consumo_l2:
                solarlink.conmutador(l1 = True, l2 = False)
            else:
                solarlink.conmutador(l1=False, l2=True)

        if consumo_l1 > trigger and consumo_l2 > trigger:
            solarlink.conmutador(l1=False, l2=False)
        elif consumo_l1 > trigger and consumo_l2 < trigger:
            solarlink.conmutador(l1=False, l2=True)
        elif consumo_l1 < trigger and consumo_l2 > trigger:
            solarlink.conmutador(l1=True, l2=False)

async def post():
    global solarlink
    if solarlink.hora_inicial != solarlink.rtc.datetime()[4]:
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
        solarlink.hora_inicial = time[4]

        r = requests.post(solarlink.url + "/user/load-data/", data=payload)



async def tiempo_real():
    global solarlink
    
    if solarlink.tiempo_real:
        payload = json.dumps({"username": solarlink.username, "password": solarlink.password})
        r = requests.get(solarlink.url + "/user/user-is-online/", data=payload)

        response = json.loads(r.text)
        
        if response["response"]:
            payload = json.dumps({"username": solarlink.username, "password": solarlink.password,
                                  "voltaje": solarlink.medicion["voltaje"],
                                  "consumo_l1": solarlink.medicion["consumo_l1"],
                                  "consumo_l2": solarlink.medicion["consumo_l2"],
                                  "solar_l1": solarlink.l1,
                                  "solar_l2": solarlink.l2})
            requests.post(solarlink.url + "/user/tiempo-real/", data = payload)
            
        solarlink.tiempo_real = False

        
async def main():
    asyncio.create_task(mediciones())
    asyncio.create_task(display())
    asyncio.create_task(conmutacion())
    asyncio.create_task(post())
    asyncio.create_task(tiempo_real())


while 1:
    asyncio.run(main())



