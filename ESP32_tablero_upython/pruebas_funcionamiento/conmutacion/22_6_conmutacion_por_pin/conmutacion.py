from machine import Pin
import time

##31 red 1, 36 red 2
#pcruce = Pin(15, Pin.IN) #Pin de entrada del cruce por cero.
pconm = Pin(31, Pin.OUT) #31 es el pin de salida del micro que controla el conmutador de una de las dos redes del conmutador.
#
#def commuter_interrupt():
#    global commuterFlag 
#    commuterFlag = 1 #Al activarse la interrupción, se coloca el flag del conmutador en 1.
#    
#pcruce.irq(trigger=3, handler=commuter_interrupt) #3 hace que la interrupción se dispare con ambos flancos.
#
#while 1:
#    if commuterFlag:
#        pconm = 1
#        commuterFlag = 0
#    else:
#        pconm = 0

while 1:
    pconm = 1
    time.sleep(2)
    pconm = 0
    time.sleep(2)