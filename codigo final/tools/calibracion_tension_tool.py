from machine import ADC, Pin
import time, math
import machine

suma = 0
index = 0

p33 = Pin(33, Pin.IN)
adc = ADC(p33)
adc.atten(ADC.ATTN_2_5DB) #atenuacion

for i in range(100):                #calibración por promedio
    ref = adc.read_uv() / 1000000
    index += 1
    suma += ref
vref = suma / index #valor de referencia promedio, en la ejecución probada es 1.0193, se usará en la variable "val"
print(vref)