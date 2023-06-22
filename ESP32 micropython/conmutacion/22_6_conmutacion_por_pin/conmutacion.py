from machine import Pin
import time

p19 = Pin(19, Pin.OUT)
p18 = Pin(18, Pin.OUT)

while 1:
    p19.on()
    p18.off()
    time.sleep(1)
    p19.off()
    p18.on()
    time.sleep(1)    
