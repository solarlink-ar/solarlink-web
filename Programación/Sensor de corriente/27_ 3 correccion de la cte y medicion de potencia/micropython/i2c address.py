import machine

sdaPIN=machine.Pin(21)
sclPIN=machine.Pin(22)

i2c=machine.I2C(sda=sdaPIN, scl=sclPIN, freq=10000) #i2c config

devices = i2c.scan() #scaneo de direcciones de los dispositivos
if len(devices) == 0:
 print("No i2c device !")
else:
 print('i2c devices found:',len(devices))
for device in devices:
 print("At address: ",hex(device))