import machine
from machine import SoftI2C, Pin
sdaPIN=machine.Pin(21)
sclPIN=machine.Pin(22)
i2c=machine.I2C(0,sda=sdaPIN, scl=sclPIN, freq=400000)
softi2c = SoftI2C(scl=Pin(27), sda=Pin(26), freq=100000)

devices = i2c.scan() #scan de disp. i2c conectados
if len(devices) == 0:
    print("No i2c device !")
else:
    print('i2c devices found:',len(devices))
for device in devices:
    print("Hexa address: ",hex(device))