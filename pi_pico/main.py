from machine import UART, Pin
import urequests
import ujson

uart1 = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))

def comm():
    data = uart1.read()