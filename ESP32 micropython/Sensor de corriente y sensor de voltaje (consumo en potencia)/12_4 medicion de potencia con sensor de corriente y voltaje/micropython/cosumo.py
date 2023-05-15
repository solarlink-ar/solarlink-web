import ads1115, math,time, machine
from machine import ADC, Pin, I2C

list = []
suma = 0
index = 0
suma2 = 0
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=400000) #i2c init
adc_e = ads1115.ADS1115(i2c, 72, 0) #adc externo init

p36 = Pin(36, Pin.IN) #pin init
adc_i = ADC(p36) #adc interno init
adc_i.atten(ADC.ATTN_2_5DB) #atenuacion adc interno


while 1:
    v_sens = adc_e.raw_to_v(adc_e.read(7, 2, 3)) #mido V del sens. corriente 
    list.append(v_sens) #apendo a lista de voltajes del sens de corriente
    
    val = adc_i.read_uv() / 1000000 * 225 / 1.0193 #mido V del sens. tension de linea rms
    suma += val #suma para el promedio
    index += 1 # index para el promedio
    
    if len(list) == 666: #si se tomaron 666 muestras del sens de corriente (aprox 2 segs)
        v_max = max(list) #tension pico del sens de corriente

        corriente = (0.485816226 * pow(v_max,3) -1.1205922* pow(v_max,2) + 5.651277 * v_max) / math.sqrt(2)  #funcion para convertir a corriente rms

        voltaje = int(suma/index) #promedio de tension de linea rms en 2 segs

        list = []
        suma = 0
        index = 0

        print(f'Voltaje: {voltaje} V ')
        print(f'Corriente: {corriente} A')
        print(f'Potencia: {voltaje * corriente} W')
        print('-------------------------------------')
        
        
        
    