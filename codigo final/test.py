from machine import Pin
from solarlink import Solarlink
import time

p13 = Pin(13, Pin.IN, pull=None)
p2 = Pin(2, Pin.OUT)

solarlink = Solarlink()

solarlink.conmutador(pin_l1 = True, pin_l2 = False)
'''
trigger = False
def callback(pin):
    global trigger
    trigger = True

p13.irq(trigger=Pin.IRQ_RISING, handler=callback)
index = 0
while 1:
    if trigger:
        index += 1
        trigger = False
    
    if index >= 50:
        index = 0
        if p2.value():
            p2.off()
        else:
            p2.on()
'''