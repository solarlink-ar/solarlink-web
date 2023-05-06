from machine import ADC, Pin
import time, math
import machine
from machine import I2C


index = 0
max = 0
list = []
index = 0
p36 = Pin(36, Pin.IN)
adc = ADC(p36)
adc.atten(ADC.ATTN_2_5DB) #atenuacion

'''
tiempo1 = time.ticks_ms()
suma = 0
'''
#variables para hacer un promedio


while 1:
    val = int(adc.read_u16() / 48500 * 222 / 0.99) #adc pasado a v de linea
    print(val)



    '''
    tiempo2 = time.ticks_ms()
    if val > max:
        max = val
    if (tiempo2 - tiempo1) / 1000 >= 0.2:
        list.append(max)
        tiempo1 = time.ticks_ms()
        max = 0
        index += 1
        
    if index == 5:
        for i in list:
            suma += i
        print(int(suma / len(list)))
        list = []
        suma = 0
        index = 0
'''
#prototipo de promedio de valores maximos medidos