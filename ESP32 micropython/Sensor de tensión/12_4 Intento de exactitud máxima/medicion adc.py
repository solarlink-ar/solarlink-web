from machine import ADC, Pin
import time, math
import machine


p36 = Pin(36, Pin.IN)
adc = ADC(p36)
adc.atten(ADC.ATTN_2_5DB) #atenuacion


tiempo1 = time.ticks_ms() #tiempo ref


suma = 0
index = 0

for i in range(100):                #calibración por promedio
    ref = adc.read_uv() / 1000000
    index += 1
    suma += ref
vref = suma / index #valor de referencia promedio, en la ejecución probada es 1.0193, se usará en la variable "val"


suma = 0
index = 0

while 1:

    val = adc.read_uv() / 1000000 * 225 / 1.0193 #voltaje de linea
    suma += val
    index += 1
    tiempo2 = time.ticks_ms()
    if (tiempo2 - tiempo1) / 1000 >= 1: #prom de 1seg del voltaje de linea
        print(int(suma/index))
        suma = 0
        index = 0
        tiempo1 = time.ticks_ms()
