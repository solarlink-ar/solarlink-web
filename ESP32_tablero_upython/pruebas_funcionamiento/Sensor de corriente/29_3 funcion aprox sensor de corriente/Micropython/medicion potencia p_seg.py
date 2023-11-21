import ads1115
from machine import I2C, Pin
import time
import math


list = []
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)     #i2c setup

adc = ads1115.ADS1115(i2c, 72, 0)                       #activo mediciones con el adc externo

while 1:
    voltaje = adc.raw_to_v(adc.read(7,0,1)) #medicion voltaje
    list.append(voltaje) #lista de voltajes
    
    if len(list) == 333: #si se tomaron 333 muestras (aprox 1 seg)
        v_max = max(list) #busco el valor mas alto
        list = []
        res = 61.13 * pow(v_max,3) + 71.33 * pow(v_max,2) + 837.51 * v_max  #cte para convertir a potencia
        print(res)
