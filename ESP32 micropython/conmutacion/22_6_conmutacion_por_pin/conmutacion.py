from machine import Pin
import time

p15 = Pin(15, Pin.IN)

def commuter_interrupt(pin)
    global commuterFlag 
    commuterFlag = 1
    
p15.irq(trigger=3, handler=commuter_interrupt)

while 1:
    if commuterFlag:
        