import machine
from machine import I2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

I2C_ADDR     = 0x27 #i2c addr
I2C_NUM_ROWS = 2 #filas del lcd
I2C_NUM_COLS = 16 #columnas del lcd

i2c = I2C(1, sda=machine.Pin(21), scl=machine.Pin(22)) #inicio i2c
lcd = I2cLcd(i2c, 0x27, 4, 20) #inicio lcd


lcd.display_on()
lcd.backlight_on()
lcd.hide_cursor()

lcd.clear()
lcd.putstr('Hello world!') #printeo en lcd