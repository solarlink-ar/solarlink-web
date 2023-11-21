from machine import UART, Pin
import time
print("test")
uart2 = UART(2, baudrate=9600, tx=17, rx=16)
# uart2.write('HOLA MUNDO')
# uart2.init()
#print("HOLA")
test = Pin(3, Pin.OUT)

print("gordo")

while 1:
    data = uart2.read()
    time.sleep(5)
    
        
        
        



