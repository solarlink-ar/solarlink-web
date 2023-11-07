import machine, time, json, math, ads1115, network
from machine import Pin, ADC, I2C, Timer, UART, RTC,
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import urequests as requests
import ntptime
import _thread

class Solarlink_post(object):
    
    ######################################################################################################
    ######################################################################################################
    ######################################## CONSTRUCTOR #################################################
    ######################################################################################################
    ######################################################################################################

    def __init__(self):
        
        #################################### USUARIO Y CONTRASEÑA ########################################

        self.username = "helyivan"
        self.password = "12345678"

        #################################### CONMUTACIÓN #################################################

        self.l1 = True
        self.l2 = True

        #################################### RTC #########################################################
        #ntptime.settime()
        
        self.rtc = RTC()
        ntptime.settime()
        tm = time.localtime(time.mktime(time.localtime()) -3*3600)
        tm = tm[0:3] + (0,) + tm[3:6] + (0,)
        self.rtc.datetime(tm)
        #self.rtc.datetime((2023, 10, 26, 3, 7, 59, 0, 0))
        print(self.rtc.datetime())

        #################################### POSTEO ######################################################

        self.acumulacion_voltaje_red = 0
        self.acumulacion_consumo_red = 0
        self.acumulacion_consumo_solar = 0

        self.acumulacion_consumo_l1_solar = 0
        self.acumulacion_consumo_l1_proveedor = 0

        self.acumulacion_consumo_l2_solar = 0
        self.acumulacion_consumo_l2_proveedor = 0

        self.indice_mediciones = 0

        #self.hora_inicial = self.rtc.datetime()[4]
        
        self.timer0 = None
        
        self.tiempo_real = False


    #####################################################################################################
    #####################################################################################################
    ########################################## METODOS ##################################################
    #####################################################################################################
    #####################################################################################################

    ##################################### CALLBACK TIMER1 ###############################################
    def callback_posteo(self, t):
        self.tiempo_real = True

    def acumulador(self, payload):
        # acumulo voltaje
        voltaje = payload["voltaje"]
        consumo_l1 = payload["consumo_l1"]
        consumo_l2 = payload["consumo_l2"]
    
        self.acumulacion_voltaje_red += voltaje

        # acumulo l1
        if self.l1:
            self.acumulacion_consumo_l1_solar += consumo_l1
            self.acumulacion_consumo_solar += consumo_l1
        else:
            self.acumulacion_consumo_l1_proveedor += consumo_l1
            self.acumulacion_consumo_red += consumo_l1
        # acumulo l2
        if self.l2:
            self.acumulacion_consumo_l2_solar += consumo_l2
            self.acumulacion_consumo_solar += consumo_l2

        else:
            self.acumulacion_consumo_l2_proveedor += consumo_l2
            self.acumulacion_consumo_red += consumo_l2
        

        self.indice_mediciones += 1
        

##'''
##    def medicion_pi_pico(self):
##        self.uart2 = UART(2, baudrate=9600, tx=17, rx=16)
##        while True:
##            rawdata = self.uart2.read() #rawdata almacena la información enviada
##            data = json.loads(rawdata)
##            volt_actual = data["volt_actual"]
##            prom_hour = data["prom_hour"]
##            self.medicion_ext = {"volt_actual": volt_actual,
##                                "prom_hour": prom_hour
##                                } #diccionario que contiene los valores a publicar
##            return self.medicion_ext
##'''



## class weblink():
##     def __init__(self):
##         self.link = ...
##     def calculos(voltaje):
## 
##     def post(self, dict):
##         
##         requests.post("", dict)


## tb = solarlinktestbench()
## tb.tb_start()


## solarlink = Solarlink()
## solarlink.init()
## print(solarlink.corriente_dif_read(0, 1))
## time.sleep(1)


    
