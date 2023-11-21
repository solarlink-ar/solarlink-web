from machine import ADC, Pin, I2C
import time, math
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import machine

suma = 0
index = 0

i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000) #i2c init
lcd = I2cLcd(i2c, 0x27, 4, 20) #inicio lcd

p33 = Pin(33, Pin.IN)
adc = ADC(p33)
adc.atten(ADC.ATTN_2_5DB) #atenuacion

for i in range(100):                #calibración por promedio
    ref = adc.read_uv() / 1000000
    index += 1
    suma += ref
vref = suma / index #valor de referencia promedio, en la ejecución probada es 1.0193, se usará en la variable "val"
lcd.putstr(f'{vref} V')

