from machine import Pin
import time

pcruce = Pin(15, Pin.IN) #Pin de entrada del cruce por cero.
pconm = Pin(1, Pin.OUT) #1 es un placeholder porque desconozco el pin del conmutador. Pendiente arreglar lo antes posible

def commuter_interrupt(pin)
    global commuterFlag 
    commuterFlag = 1 #Al activarse la interrupción, se coloca el flag del conmutador en 1.
    
pcruce.irq(trigger=3, handler=commuter_interrupt) #3 hace que la interrupción se dispare con ambos flancos.

while 1:
    if commuterFlag:
        pconm = 1
        commuterFlag = 0
    else:
        pconm = 0
