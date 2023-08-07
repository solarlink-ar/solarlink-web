import machine, time, json, math, ads1115, network
from machine import Pin, ADC, I2C, Timer
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import urequests as requests


class Solarlink(object):
    def __init__(self):
        self.i2c_corriente_dir = 72
        self.scl = 22
        self.sda = 21
        self.freq = 400000
        self.gain = 0
        self.pendiente_corriente = 10.1288571642
        #################
        self.adc_pin = 33
        self.atten = ADC.ATTN_2_5DB
        self.ref = 222 / 0.9580893
        
    def init(self):
        self.i2c = I2C(1, scl=Pin(self.scl), sda=Pin(self.sda), freq=self.freq) #i2c init
        self.ads1115 = ads1115.ADS1115(self.i2c, self.i2c_corriente_dir, self.gain) #adc externo init
        port = Pin(self.pin, Pin.IN) #pin init
        self.adc = ADC(port)
        self.adc.atten(self.atten)
    
        
    def corriente_dif_read(self, pin_a, pin_b):
        medicion = self.ads1115.raw_to_v(self.ads1115.read(7, pin_a, pin_b))
        corriente = self.pendiente_corriente * medicion / math.sqrt(2)
        return corriente

    def voltaje_read(self):
        voltaje = self.adc.read_uv() / 1000000 * self.ref # mido V del sens. tension de linea rms
        return voltaje
    
Solarlink.init()
print(Solarlink.corriente_dif_read(0, 1))
time.sleep(1)
    
    