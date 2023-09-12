from machine import UART, Pin
import time
uart1 = UART(2, baudrate=9600, tx=Pin(28), rx=Pin(27))
# uart1.write('HOLA MUNDO')
test = Pin(35, Pin.OUT)


while 1:
    uart1.write("puto")
    time.sleep(5)
    if("hola" in uart1.read()):
        test = 1
        time.sleep(5)
        test = 0
        break
        
        


