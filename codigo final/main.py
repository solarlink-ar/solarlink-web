from solarlink import Solarlink
import machine, time, json, math, ads1115, network
from machine import Pin, ADC, I2C, Timer, UART
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import urequests as requests
import _thread




#
#
suma_adc_e = 0
suma_adc_i = 0
index = 0
valores_sens_corriente = []
sens_corriente_1 = 0
sens_corriente_2 = 0
timercount = False
#
#

def values_restart():
    global suma_adc_e
    global suma_adc_i
    global index
    global valores_sens_corriente
    global sens_corriente_1
    global sens_corriente_2
    suma_adc_e = 0
    suma_adc_i = 0
    index = 0
    valores_sens_corriente = []
    sens_corriente_1 = 0
    sens_corriente_2 = 0

#
def callback_web(tim1): #minute callback
    global timercount
    timercount = True
#
#
tim1 = Timer(1)
tim1.init(period=2000, mode=Timer.PERIODIC, callback=callback_web) #timer init
#
#
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

'''
while 1:
    print(solarlink.medicion_default_segundo())
'''
while 1:
    corriente_actual_1 = solarlink.corriente_dif_read(2, 3)
    if corriente_actual_1 > sens_corriente_1:
        sens_corriente_1 = corriente_actual_1
        
    corriente_actual_2 = solarlink.corriente_dif_read(0, 1)
    if corriente_actual_2 > sens_corriente_2:
        sens_corriente_2 = corriente_actual_2
    
    #
    #
    voltaje_actual = solarlink.voltaje_read() # mido V del sens. tension de linea rms
    suma_adc_i += voltaje_actual
    index += 1 # index para el promedio
    #
    #
    if timercount:
        solarlink.lcd.clear()
        sens_voltaje = int(suma_adc_i/index)
        consumo_1 = sens_voltaje * sens_corriente_1
        consumo_2 = sens_voltaje * sens_corriente_2
        #
        #

        if sens_voltaje <= 80:
            solarlink.lcd.move_to(0, 0)
            solarlink.lcd.putstr('Vin: NULO O ERROR V')
            solarlink.lcd.move_to(0,1)
            solarlink.lcd.putstr("LINEA1")
            solarlink.lcd.move_to(14, 1)
            solarlink.lcd.putstr("LINEA2")
            
            solarlink.lcd.move_to(0,2)
            solarlink.lcd.putstr('%.2f A' % (sens_corriente_1))
            solarlink.lcd.move_to(14, 2)
            solarlink.lcd.putstr('%.2f A' % (sens_corriente_2))
            
            solarlink.lcd.move_to(1,3)
            solarlink.lcd.putstr('CONSUMO BAJO POR V')
        else:
            solarlink.lcd.move_to(5, 0)
            solarlink.lcd.putstr(f'Vin:{sens_voltaje} V')

            solarlink.lcd.move_to(0,2)
            solarlink.lcd.putstr('%.2f A' % (sens_corriente_1))
            solarlink.lcd.move_to(14, 2)
            solarlink.lcd.putstr('%.2f A' % (sens_corriente_2))
            
            solarlink.lcd.move_to(0,3)
            solarlink.lcd.putstr(f'{int(consumo_1)} W')
            solarlink.lcd.move_to(14, 3)
            solarlink.lcd.putstr(f'{int(consumo_2)} W')

        timercount = False
        values_restart()
    


#############
#### WIP ####
#############

'''
##Permite bloquear la ejecución de otras partes del código mientras se está ejecutando el thread seleccionado.
##Funciona como un semáforo binario.

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