from machine import ADC, Pin
import time, math

list = []
index = 0
suma = 0
p36 = Pin(36, Pin.IN)
adc = ADC(p36)
adc.atten(ADC.ATTN_11DB) #atenuacion adc

tiempo1 = time.ticks_ms() #tiempo de referencia
while 1:
    val = adc.read_uv() / 1000000 * 225 / 3.1 #leo adc y calculo eq. en V de linea
    index += 1
    suma += val #suma para sacar un promedio
    tiempo2 = time.ticks_ms()
    if (tiempo2 - tiempo1) / 1000 >= 1: #si pasó 1 seg...
        prom = suma / index #saco promedio
        print(prom)
        index = 0
        suma = 0
        tiempo1 = time.ticks_ms() #reestablezco referencia
