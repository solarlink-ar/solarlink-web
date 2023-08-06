import machine, time, json, math, ads1115, network
from machine import Pin, ADC, I2C, Timer
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import urequests as requests


class Triangle (Shape):
    def __init__ (self, base, altura):
        self.base = base
        self.altura = altura

specs = {	"i2c_dir": 72,
            "scl": 22,
            "sda": 21,
            "freq": 400000,
            "gain": 0,
            "pendiente_corriente": 10.1288571642
        }

class corriente(object):
    def __init__(self, specs):
        self.i2c_dir = specs["i2c_dir"]
        self.scl = specs["scl"]
        self.sda = specs["sda"]
        self.freq = specs["freq"]
        self.gain = specs["gain"]
        self.pendiente_corriente = specs["pendiente_corriente"]
    
    def init(self):
        i2c = I2C(1, scl=Pin(self.scl), sda=Pin(self.sda), freq=self.freq) #i2c init
        adc = ads1115.ADS1115(i2c, self.i2c_dir, self.gain) #adc externo init
        return adc
        
    def dif_read(self, adc, pin_a, pin_b):
        medicion = adc.raw_to_v(adc_e.read(7, pin_a, pin_b))
        corriente = self.pendiente_corriente * medicion / math.sqrt(2)
        return corriente

specs = {	"pin": 33,
            "atten": ADC.ATTN_2_5DB,
            "ref": 222 / 0.9580893
        }

class voltaje(object):
    def __init__(self, specs):
        self.pin = specs["pin"]
        self.atten = specs["atten"]
        self.ref = specs["ref"]
        
    def init(self):
        port = Pin(self.pin, Pin.IN) #pin init
        adc = ADC(port)
        adc.atten(self.atten)
        return adc
    
    def read(self, adc):
        voltaje = adc.read_uv() / 1000000 * self.ref # mido V del sens. tension de linea rms
        return voltaje
    
        
        
        
sensor = voltaje.init(specs)
valor = voltaje.read(sensor)


        
        

        
        
        
        
        