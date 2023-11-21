import ads1115
from machine import I2C, Pin
import time

list = []
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000) #i2c setup

adc = ads1115.ADS1115(i2c, 72, 0) #activo mediciones con el adc externo


while len(list) < 20:
    voltaje = adc.raw_to_v(adc.read(6,0,1))
    list.append(voltaje)
    time.sleep_ms(1)

maximo = max(list)
print(maximo)
print(list)

'''
voltaje = adc.raw_to_v(adc.read(6,0,1)) #calculo de voltaje, samples default, canal 0
print(voltaje)
'''
