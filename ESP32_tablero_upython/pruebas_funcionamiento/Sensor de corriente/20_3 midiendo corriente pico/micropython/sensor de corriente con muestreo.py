import ads1115
from machine import I2C, Pin
import time
import math


list = []
maximos_voltajes = []
voltaje = 0
maximo = 0
res = 0
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000)     #i2c setup

adc = ads1115.ADS1115(i2c, 72, 0)                       #activo mediciones con el adc externo

for _ in range(10):                                     #10 muestras de señales
    while len(list) < 20:                               #20 muestras de voltaje
        voltaje = adc.raw_to_v(adc.read(7,0,1))         #paso a voltaje
        list.append(voltaje)                            #añado a la lista de voltajes de esta muestra
    maximo = max(list)                                  #saco el maximo de esta muestra
    maximos_voltajes.append(maximo)                     #lo apendo a la lista de máximos de muestra de señales
    list = []                                           #vacio la lista de muestras de voltaje

res = max(maximos_voltajes) * 820                       #calculo la corriente en eficaz
print(res)

