import machine, time, json, math, ads1115, network
from machine import Pin, ADC, I2C, Timer
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import urequests as requests
#
#
suma_adc_e = 0
suma_adc_i = 0
index = 0
valores_sens_corriente = []
v_max_1 = 0
v_max_2 = 0
timercount = False
#
#
def calculo_corriente(v_max):
    return ((8.65714286 * v_max) / math.sqrt(2)) * 1.17 #10.1288571642
#
#
def values_restart():
    global suma_adc_e
    global suma_adc_i
    global index
    global valores_sens_corriente
    global v_max_1
    global v_max_2
    suma_adc_e = 0
    suma_adc_i = 0
    index = 0
    valores_sens_corriente = []
    v_max_1 = 0
    v_max_2 = 0
#
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
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000) #i2c init
adc_e = ads1115.ADS1115(i2c, 72, 0) #adc externo init

p33 = Pin(33, Pin.IN) #pin init
adc_i = ADC(p33) #adc interno init
adc_i.atten(ADC.ATTN_2_5DB) #atenuacion adc interno
#
#
lcd = I2cLcd(i2c, 0x27, 4, 20) #inicio lcd
#
#
while 1:
    v_act_sens_i_1 = adc_e.raw_to_v(adc_e.read(7,2,3))
    if v_act_sens_i_1 > v_max_1:
        v_max_1 = v_act_sens_i_1
        
    v_act_sens_i_2 = adc_e.raw_to_v(adc_e.read(7,0,1))
    if v_act_sens_i_2 > v_max_2:
        v_max_2 = v_act_sens_i_2
    
    #
    #
    v_act_sens_v = adc_i.read_uv() / 1000000 * 222 / 0.9580893 # mido V del sens. tension de linea rms
    suma_adc_i += v_act_sens_v
    index += 1 # index para el promedio
    #
    #
    if timercount:
        lcd.clear()
        sens_corriente_1 = calculo_corriente(v_max_1)
        sens_corriente_2 = calculo_corriente(v_max_2)
        sens_voltaje = int(suma_adc_i/index)
        consumo_1 = sens_voltaje * sens_corriente_1
        consumo_2 = sens_voltaje * sens_corriente_2
        #
        #
        lcd.move_to(5, 0)
        lcd.putstr(f'Vin:{sens_voltaje} V')
        lcd.move_to(0,1)
        lcd.putstr("LINEA1")
        lcd.move_to(0,2)
        lcd.putstr('%.2f A' % (sens_corriente_1))
        lcd.move_to(0,3)
        lcd.putstr(f'{int(consumo_1)} W')
        lcd.move_to(14, 1)
        lcd.putstr("LINEA2")
        lcd.move_to(14, 2)
        lcd.putstr('%.2f A' % (sens_corriente_2))
        lcd.move_to(14, 3)
        lcd.putstr(f'{int(consumo_2)} W')
        #
        #
        #post_data = json.dumps({'sens_voltaje': sens_voltaje, 'sens_corriente': sens_corriente, 'consumo': consumo})
        #requests.get('https://helyivan.pythonanywhere.com/datos', data = post_data)
        timercount = False
        values_restart()
    
