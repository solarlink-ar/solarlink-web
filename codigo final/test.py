from machine import Pin
from solarlink import Solarlink
import time

p13 = Pin(13, Pin.IN, pull=None)
p2 = Pin(2, Pin.OUT)
'''
#solarlink = Solarlink()

#solarlink.conmutador(pin_l1 = True, pin_l2 = False)

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

p13 = Pin(13, Pin.IN)


def callback(pin):
    print('hola')
    pin_l1 = Pin(19, Pin.OUT)
    pin_l2 = Pin(18, Pin.OUT)
    time.sleep_ms(10)
    pin_l1.on()
    pin_l2.on()

p13.irq(trigger=Pin.IRQ_RISING, handler=callback)

while 1:
    pass
    


