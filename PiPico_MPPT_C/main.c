#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"

#define PWM_WRAP                        3787  // Definimos frecuencia del micro, sin prescaler, 33kHz

//cambiar configuracion ADC

#define ADC_GPIO_BATTERY                28 
#define ADC_CURRENT_BATTERY             29 
#define ADC_OUT                         27 
#define ADC_CHANNEL_BATTERY             2 
#define ADC_CURRENT_CHANNEL_BATTERY     3
#define ADC_CHANNEL_OUT                 1

#define BATTERY_ADC_RATIO               5     // Habra un ratio de 5 a 1 en el voltaje leido por el ADC y la bat

#define BULK_MAX_BATTERY_VOLTAGE        14.4
#define BULK_MAX_CURRENT_VOLTAGE        6000

#define ABSORTION_MAX_BATTERY_VOLTAGE   14.6   // Umbral de tension del modo ABSORTION
#define ABSORTION_MAX_PANEL_CURRENT     6000
#define ABSORTION_MIN_PANEL_CURRENT     300

#define FLOAT_MAX_BATTERY_VOLTAGE       13.8
#define FLOAT_MIN_BATTERY_VOLTAGE       13.5
#define FLOAT_MAX_CURRENT_VOLTAGE       350
 
#define BATTERY_MIN_VOLTAGE     12.9       

float battery_voltage = 0;
float battery_current = 0;
float x = 0;

typedef enum {
    BULK_MODE,
    ABSORTION_MODE,
    FLOAT_MODE
} charging_mode_t;

// Saturador basico, se asegura que el PWM no sea ni negativo ni que se exceda del wrap
inline static uint16_t saturador(uint16_t wrap, int16_t level) {
    if(level > PWM_WRAP) {
        return PWM_WRAP;
    }
    else if(level < 0) {
        return 0;
    }
    return level;
}

float med_volt(value){
    float prom = 0;
    for (int i = 0; i < 10; i++){
        float volt = BATTERY_ADC_RATIO * adc_read() * 3.3 / (1 << 12);
        prom = prom + volt;
        }
    return prom/10
}

float med_current(value){
    float prom = 0;
    for (int i = 0; i < 10; i++){
        float current = ((BATTERY_ADC_RATIO * adc_read() * 3.3 / (1 << 12)) - 2.515) * (-10);
        prom = prom + current;
    }
    return prom/10
}

int main() {
    /* Inicializa el standard input/output de la pico */
    stdio_init_all();
    
    uint8_t pwm = 11;
    uint8_t slice = pwm_gpio_to_slice_num(pwm);
    int16_t pwm_level = PWM_WRAP / 2;

    // Se define el modo inicial como BULK
    charging_mode_t charging_mode = BULK_MODE;

    // Inicializacion del ADC
    adc_init();
    adc_gpio_init(ADC_GPIO_BATTERY);
    adc_gpio_init(ADC_CURRENT_BATTERY);
    adc_select_input(ADC_CHANNEL_BATTERY);


    // Habilito GPIO como salida de PWM
    gpio_set_function(pwm, GPIO_FUNC_PWM);
    // Wrap para 33 KHz de PWM a 125 MHz de clock
    pwm_set_wrap(slice, PWM_WRAP);
    // 50% de ancho de pulso de partida
    pwm_set_gpio_level(pwm, pwm_level);
    // Habilitar PWM
    pwm_set_enabled(slice, true);

    while (true) {
        // Selecciono el canal de la tension y se lee y se convierte
        adc_select_input(ADC_CHANNEL_BATTERY);
        battery_voltage = med_volt(x);
        printf("voltaje = %d", battery_voltage);
        // Selecciono el canal de la corriente y se lee y se convierte
        adc_select_input(ADC_CURRENT_CHANNEL_BATTERY);
        battery_current = med_current(x);
        printf("corriente = %d", battery_current);
'''
    ///////////////   MDOE VERIFICATION   ///////////////    
        if (charging_mode == BULK_MODE){
            if (battery_voltage > BULK_MAX_BATTERY_VOLTAGE) {
                    // Cambio modo de carga en caso de que corriente baje del umbral
                    charging_mode = ABSORTION_MODE;
                }
        }
        if (charging_mode == ABSORTION_MODE){
            if (battery_current < ABSORTION_MIN_PANEL_CURRENT) {
                    // Cambio modo de carga en caso de que corriente baje del umbral
                    charging_mode = FLOAT_MODE;
                }
        }
        if (charging_mode == FLOAT_MODE){
            if (battery_voltage < FLOAT_MIN_BATTERY_VOLTAGE) {
                    charging_mode = BULK_MODE;
                }  
            if (battery_current > FLOAT_MAX_CURRENT_VOLTAGE) {
                    // Cambio modo de carga en caso de que corriente exceda umbral
                    charging_mode = BULK_MODE;
                }
        }
    ///////////////   END MDOE VERIFICATION   ///////////////   
    
    ///////////////   BULK   ///////////////
    
        if (charging_mode == BULK_MODE) {
            if (battery_current > BULK_MAX_CURRENT_VOLTAGE) {
                pwm_level--;
            }
            else {
                pwm_level++;
            }
            // Verifico que no exceda los limites
            pwm_level = saturador(PWM_WRAP, pwm_level);
            // Ajusto PWM
            pwm_set_gpio_level(slice, pwm_level);

        }

    ///////////////   END BULK   ///////////////
    
    ///////////////   ABSORTION   ///////////////
        if (charging_mode == ABSORTION_MODE)  {
            if(battery_current > ABSORTION_MAX_PANEL_CURRENT) {
                pwm_level--;
            }  
            else if(battery_voltage > ABSORTION_MAX_BATTERY_VOLTAGE) {
                // Incremento el duty en una unidad
                pwm_level++;
            }
            else {
                pwm_level--;
            }
            // Verifico que no exceda los limites
            pwm_level = saturador(PWM_WRAP, pwm_level);
            // Ajusto PWM
            pwm_set_gpio_level(slice, pwm_level);
        }
    ///////////////  END ABSORTION  ////////////////

    ///////////////  FLOAT  ////////////////
        if(charging_mode == FLOAT_MODE) {
            if (battery_voltage > FLOAT_MAX_BATTERY_VOLTAGE){
                pwm_level--;
            }
            else {
                pwm_level++;
            }
            // Verifico que no exceda los limites
            pwm_level = saturador(PWM_WRAP, pwm_level);
            // Ajusto PWM
            pwm_set_gpio_level(slice, pwm_level);
            
        }
    ///////////////  END FLOAT  ////////////////
    }
    return 0;
    '''
}


//fijarse voltaje ref de adc