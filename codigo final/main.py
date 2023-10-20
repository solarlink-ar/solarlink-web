from solarlink import Solarlink
import machine, time, json, math, ads1115, network
from machine import Pin, ADC, I2C, Timer, UART
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import urequests as requests
import _thread

p2 = Pin(2, Pin.OUT)
#pin_l1 = Pin(19, Pin.OUT)
#pin_l2 = Pin(18, Pin.OUT)
#pin_cruce = Pin(13, Pin.IN
'''wlan = network.WLAN(network.STA_IF) #network init
wlan.active(True)
while not wlan.isconnected():
    try:
        wlan.connect('Red Alumnos', '') #network connection
    except:
        pass'''

#
#
solarlink = Solarlink()
#
#


while 1:
    valores = solarlink.medicion_default_segundo()

    solarlink.lcd.move_to(5, 0)
    solarlink.lcd.putstr(f'Vin:{valores["voltaje"]} V')
    solarlink.lcd.move_to(0,1)
    solarlink.lcd.putstr("LINEA1")
    solarlink.lcd.move_to(0,2)
    solarlink.lcd.putstr('%.2f A' % (valores["corriente_l1"]))
    solarlink.lcd.move_to(0,3)
    solarlink.lcd.putstr('{:0>4d} W'.format(valores["consumo_l1"]))
    solarlink.lcd.move_to(14, 1)
    solarlink.lcd.putstr("LINEA2")
    solarlink.lcd.move_to(14, 2)
    solarlink.lcd.putstr('%.2f A' % (valores["corriente_l2"]))
    solarlink.lcd.move_to(14, 3)
    solarlink.lcd.putstr('{:0>4d} W'.format(valores["consumo_l2"]))
    
    
    voltaje = valores["voltaje"]
    corriente_l1 = valores["corriente_l1"]
    corriente_l2 = valores["corriente_l2"]
    consumo_l1 = valores["consumo_l1"]
    consumo_l2 = valores["consumo_l2"]

    #p_l1.off()
    #p_l2.off()
    
    trigger = solarlink.trigger
    
    # logica de conmutacion
    if consumo_l1 + consumo_l2 < trigger:
        solarlink.conmutador(l1 = True, l2 = True)
    else:
        if consumo_l1 < trigger and consumo_l2 < trigger:
            if consumo_l1 > consumo_l2:
                solarlink.conmutador(l1 = True, l2 = False)
                #p_l1.on()
                #p_l2.off()
            else:
                solarlink.conmutador(l1=False, l2=True)
                #p_l1.off()
                #p_l2.on()
        if consumo_l1 > trigger and consumo_l2 > trigger:
            solarlink.conmutador(l1=False, l2=False)
            #p_l1.off()
            #p_l2.off()
        elif consumo_l1 > trigger and consumo_l2 < trigger:
            solarlink.conmutador(l1=False, l2=True)
            #p_l1.off()
            #p_l2.on()
        elif consumo_l1 < trigger and consumo_l2 > trigger:
            solarlink.conmutador(l1=True, l2=False)
            #p_l1.on()
            #p_l2.off()
    
'''  
#############
#### WIP ####
#############
'''

##Permite bloquear la ejecución de otras partes del código mientras se está ejecutando el thread seleccionado.
##Funciona como un semáforo binario.
'''
def threadCommWeb():
    test = 0
    while True:
        
        test = True
        while test:
            uart2.write("maxi puto")
            rawdata = uart2.read() #nefastius almacena la información enviada
            data = json.loads(rawdata)
            voltaje = data["volt_actual"]
            consumo = data["prom_hour"]
            test = 0
            return voltaje, consumo


_thread.start_new_thread(threadCommWeb, ())

'''

#############
#### WIP ####
#############
