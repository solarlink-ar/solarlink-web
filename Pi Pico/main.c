#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pwm.h"

#define PWM_WRAP                3787  // Definimos frecuencia del micro, sin prescaler, 33kHz
#define ADC_GPIO_BATTERY        26
#define ADC_CURRENT_BATTERY     27
#define ADC_CHANNEL_BATTERY     0
#define ADC_CURRENT_CHANNEL_BATTERY 1

#define BATTERY_ADC_RATIO       5     // Habra un ratio de 5 a 1 en el voltaje leido por el ADC y la bat

#define BULK_MAX_BATTERY_VOLTAGE    14
#define BULK_MAX_CURRENT_VOLTAGE    2000

#define ABSORTION_MAX_BATTERY_VOLTAGE   13.8   // Umbral de tension del modo ABSORTION
#define ABSORTION_MAX_PANEL_CURRENT     2000
#define ABSORTION_MIN_PANEL_CURRENT     100

#define FLOAT_MAX_BATTERY_VOLTAGE       12.8
#define FLOAT_MIN_BATTERY_VOLTAGE       12
#define FLOAT_MAX_CURRENT_VOLTAGE       110

#define 
#define BATTERY_MIN_VOLTAGE     11.8       
#define 

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

int main() {
    /* Inicializa el standard input/output de la pico */
    stdio_init_all();
    
    uint8_t pwm = 22;
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
        float battery_voltage = BATTERY_ADC_RATIO * adc_read() * 3.3 / (1 << 12);
        // Selecciono el canal de la corriente y se lee y se convierte
        adc_select_input(ADC_CURRENT_BATTERY);
        float battery_current = adc_read() * nose;

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
            if (battery_voltage < FLOAT_MIN_BATTERY_VOLTAGE){
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
}


//fijarse voltaje ref de adc