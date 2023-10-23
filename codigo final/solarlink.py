import machine, time, json, math, ads1115, network
from machine import Pin, ADC, I2C, Timer, UART
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
import urequests as requests
import _thread

class Solarlink(object):
    
    ######################################################################################################
    ######################################################################################################
    ######################################## CONSTRUCTOR #################################################
    ######################################################################################################
    ######################################################################################################

    def __init__(self):

        ################################### ADC EXTERNO PARAMS ###########################################

        # direccion i2c ADC externo
        self.i2c_corriente_dir = 72
        # scl
        self.scl = 22
        # sda
        self.sda = 21
        # freq i2c
        self.freq = 400000
        # gain sensor
        self.gain = 0
        # pendiente de sensor de corriente
        self.pendiente_corriente = 10.1288571642

        ################################### ADC INTERNO PARAMS ###########################################

        # pin adc sensor voltaje
        self.adc_pin = 33
        # atenuacion ADC
        self.atten = ADC.ATTN_2_5DB
        # referencia sensor voltaje
        self.ref = 221 / 0.5150402

        ######################################### INITS ##################################################

        # i2c init
        self.i2c = I2C(1, scl=Pin(self.scl), sda=Pin(self.sda), freq=self.freq)
        # ADC externo init
        self.ads1115 = ads1115.ADS1115(self.i2c, self.i2c_corriente_dir, self.gain)
        # ADC en el pin init
        self.adc = ADC(Pin(self.adc_pin, Pin.IN))
        # atenuacion ADC
        self.adc.atten(self.atten)
        # display init
        self.lcd = I2cLcd(self.i2c, 0x27, 4, 20)


        ################################# TIMER Y CALLBACK ATTR ##########################################

        # timer 0
        self.timer0 = None
        # trigger fin mediciones
        self.fin_mediciones = False

        
        ################################## MEDICION POR SEG ATTR #########################################

        # medicion final
        self.medicion = None

        #################################### CONMUTACION #################################################
        
        self.pin_l1 = Pin(19, Pin.OUT)
        self.pin_l2 = Pin(18, Pin.OUT)
        self.pin_cruce = Pin(13, Pin.IN, pull=None)
        self.pin_cruce.irq(trigger=Pin.IRQ_RISING, handler=self.callback_conmutacion)

        self.trigger = 750

        self.pedido_conmutacion = False

        self.l1 = True
        self.l2 = True
        
        #################################### USUARIO Y CONTRASEÑA #######################################

        self.username = False
        self.password = False



    #####################################################################################################
    #####################################################################################################
    ########################################## METODOS ##################################################
    #####################################################################################################
    #####################################################################################################


    ##################################### CALLBACK TIMER0 ###############################################

    def callback_fin_mediciones(self, t):
        self.fin_mediciones = True
    
    ##################################### CALLBACK CONMUT ###############################################
    
    def callback_conmutacion(self, pin):
        if self.pedido_conmutacion:
            # espero 10ms, tiempo de conmutacion del relé
            time.sleep_ms(10)
            # switcheo pines al estado elegido
            self.pin_l1(self.l1)
            self.pin_l2(self.l2)
            self.pedido_conmutacion = False
    
    ############################### CORRIENTE ADC EN DIFERENCIAL ########################################

    # medicion de sensor de corriente en el instante 
    def corriente_dif_read(self, pin_a, pin_b):
        # medicion sensor de corriente con ADC externo
        medicion = self.ads1115.raw_to_v(self.ads1115.read(7, pin_a, pin_b))
        # traspaso a RMS
        corriente = self.pendiente_corriente * medicion / math.sqrt(2)

        return corriente

    ##################################### VOLTAJE ADC INTERNO ###########################################

    # medicion de sensor de voltaje en el instante
    def voltaje_read(self):
        # mido sensor de voltaje en el pin ADC, valor en RMS
        voltaje = self.adc.read_uv() / 1000000 * self.ref

        return voltaje
    
    ################################### MEDICION COMPLETA 1 SEG #########################################

    def medicion_default_segundo(self):

        # timer 0 init, timer de fin de mediciones
        self.timer0 = Timer(0).init(period=1000, mode=Timer.ONE_SHOT, callback=self.callback_fin_mediciones)

        # pico de corriente en ambas lineas (l1, l2) en el tiempo de medicion
        pico_corriente_l1 = 0
        pico_corriente_l2 = 0
        # suma de valores de voltaje para promediar
        suma_voltaje = 0
        # index para promediar
        index = 0
        
        while True:
            suma_voltaje += self.voltaje_read()
            index += 1

            # mido sensores de corriente
            corriente_actual_l1 = self.corriente_dif_read(2, 3)
            corriente_actual_l2 = self.corriente_dif_read(0, 1)

            # si la corriente medida es mas alta que el pico previo, sobreescribo
            if corriente_actual_l1 > pico_corriente_l1:
                pico_corriente_l1 = corriente_actual_l1
            # repito en linea 2
            if corriente_actual_l2 > pico_corriente_l2:
                pico_corriente_l2 = corriente_actual_l2

            # si corta el timer
            if self.fin_mediciones:
                # saco promedio de voltaje
                voltaje = suma_voltaje / index
                # saco corriente linea 1 y 2
                corriente_l1 = pico_corriente_l1
                corriente_l2 = pico_corriente_l2
                
                # calculo consumo linea 1 y 2
                consumo_l1 = voltaje * corriente_l1
                consumo_l2 = voltaje * corriente_l2
                
                # guardo en el atributo la medicion
                self.medicion = {"voltaje": int(voltaje), #voltaje de la línea
                                "corriente_l1": round(corriente_l1, 2), #corriente línea 1
                                "corriente_l2": round(corriente_l2, 2), #corriente línea 2
                                "consumo_l1": int(consumo_l1), #consumo línea 1
                                "consumo_l2": int(consumo_l2) #consumo línea 2
                                }
                
                # reinicio variables                
                pico_corriente_l1 = 0
                pico_corriente_l2 = 0
                suma_voltaje = 0
                index = 0
                
                # reinicio la variable de callback
                self.fin_mediciones = False
                # rompo el bucle y retorno
                return self.medicion
            
    ################################### CONMUTADOR DE LINEAS #########################################
    
    def conmutador(self, l1, l2):
        self.pedido_conmutacion = True
        self.l1 = l1
        self.l2 = l2
    

'''
    def medicion_pi_pico(self):
        self.uart2 = UART(2, baudrate=9600, tx=17, rx=16)
        while True:
            rawdata = self.uart2.read() #rawdata almacena la información enviada
            data = json.loads(rawdata)
            volt_actual = data["volt_actual"]
            prom_hour = data["prom_hour"]
            self.medicion_ext = {"volt_actual": volt_actual,
                                "prom_hour": prom_hour
                                } #diccionario que contiene los valores a publicar
            return self.medicion_ext
'''



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


    
