#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pico/binary_info.h"
#include "hardware/i2c.h"
#include "hardware/pwm.h"
#include "hardware/adc.h"
#include "hardware/irq.h"
#include "hardware/uart.h"
#include <cJSON.h>


#define PWM_WRAP                        3787  // Definimos frecuencia del micro, sin prescaler, 33kHz
#define ADC_GPIO_BATTERY                26
#define ADC_IN                          27
#define ADC_CURRENT_BATTERY             28
#define ADC_CHANNEL_BATTERY             0
#define ADC_CHANNEL_IN                  1
#define ADC_CURRENT_CHANNEL_BATTERY     2

#define BATTERY_ADC_RATIO               5.5     // Habra un ratio de 5 a 1 en el voltaje leido por el ADC y la bat
#define BATTERY_IN_RATIO                14.8    

#define BULK_MAX_BATTERY_VOLTAGE        14.5
#define BULK_MAX_CURRENT_VOLTAGE        4

#define ABSORTION_MAX_BATTERY_VOLTAGE   14.5   // Umbral de tension del modo ABSORTION
#define ABSORTION_MAX_PANEL_CURRENT     4
#define ABSORTION_MIN_PANEL_CURRENT     0.2

#define FLOAT_MAX_BATTERY_VOLTAGE       13.5
#define FLOAT_MIN_BATTERY_VOLTAGE       12
#define FLOAT_MAX_CURRENT_VOLTAGE       0.6

#define SPIKE_BAT                       15
 
#define BATTERY_MIN_VOLTAGE             11.5     

#define INTEGRAL_CONSTANT               3  

// Modes for lcd_send_byte
#define LCD_CHARACTER  1
#define LCD_COMMAND    0

#define MAX_LINES      4
#define MAX_CHARS      20

#define PICO_DEFAULT_I2C_SDA_PIN    4
#define PICO_DEFAULT_I2C_SCL_PIN    5


#define UART_ID     uart0
#define BAUD_RATE   115200
#define DATA_BITS   8
#define STOP_BITS   1
#define PARITY      UART_PARITY_NONE

#define UART_TX_PIN 1
#define UART_RX_PIN 2

float prom_minute = 0;
float prom_hour = 0;
float real_prom = 0;
int cont_minute = 0; 
int cont_hour = 0;

volatile bool spike_flag = 0;

float battery_in = 0;
float battery_voltage = 0;
float battery_current = 0;
float x = 0;

char str [8];
char json[14];

// commands
const int LCD_CLEARDISPLAY = 0x01;
const int LCD_RETURNHOME = 0x02;
const int LCD_ENTRYMODESET = 0x04;
const int LCD_DISPLAYCONTROL = 0x08;
const int LCD_CURSORSHIFT = 0x10;
const int LCD_FUNCTIONSET = 0x20;
const int LCD_SETCGRAMADDR = 0x40;
const int LCD_SETDDRAMADDR = 0x80;

// flags for display entry mode
const int LCD_ENTRYSHIFTINCREMENT = 0x01;
const int LCD_ENTRYLEFT = 0x02;

// flags for display and cursor control
const int LCD_BLINKON = 0x01;
const int LCD_CURSORON = 0x02;
const int LCD_DISPLAYON = 0x04;

// flags for display and cursor shift
const int LCD_MOVERIGHT = 0x04;
const int LCD_DISPLAYMOVE = 0x08;

// flags for function set
const int LCD_5x10DOTS = 0x04;
const int LCD_2LINE = 0x08;
const int LCD_8BITMODE = 0x10;

// flag for backlight control
const int LCD_BACKLIGHT = 0x08;

const int LCD_ENABLE_BIT = 0x04;

// By default these LCD display drivers are on bus address 0x27
static int addr = 0x27;


void on_uart_rx() {
    while (uart_is_readable(UART_ID)) {
        if (uart_is_writable(UART_ID)) {
            real_prom = prom_hour / cont_hour;
            sprintf(json, "{\"prom_hour\":%f,\"volt_actual\":%f}", real_prom, battery_voltage);
            uart_putc(UART_ID, *json);
        }
    }
}

int64_t alarm_callback(alarm_id_t id, void *user_data) {
    if(cont_minute < 60){
        prom_minute += (battery_in * battery_current);
        cont_minute += 1;
    }
    else{
        prom_hour += (prom_minute / cont_minute);
        cont_hour += 1;
        cont_minute = 0;
    }
    return 0;
}

/* Quick helper function for single byte transfers */
void i2c_write_byte(uint8_t val) {
#ifdef i2c_default
    i2c_write_blocking(i2c_default, addr, &val, 1, false);
#endif
}

void lcd_toggle_enable(uint8_t val) {
    // Toggle enable pin on LCD display
    // We cannot do this too quickly or things don't work
#define DELAY_US 600
    sleep_us(DELAY_US);
    i2c_write_byte(val | LCD_ENABLE_BIT);
    sleep_us(DELAY_US);
    i2c_write_byte(val & ~LCD_ENABLE_BIT);
    sleep_us(DELAY_US);
}

// The display is sent a byte as two separate nibble transfers
void lcd_send_byte(uint8_t val, int mode) {
    uint8_t high = mode | (val & 0xF0) | LCD_BACKLIGHT;
    uint8_t low = mode | ((val << 4) & 0xF0) | LCD_BACKLIGHT;

    i2c_write_byte(high);
    lcd_toggle_enable(high);
    i2c_write_byte(low);
    lcd_toggle_enable(low);
}

void lcd_clear(void) {
    lcd_send_byte(LCD_CLEARDISPLAY, LCD_COMMAND);
}

// go to location on LCD
void lcd_set_cursor(int line, int position) {
    int line_offsets[] = { 0x00, 0x40, 0x14, 0x54 };
    int val = 0x80 + line_offsets[line] + position;
    lcd_send_byte(val, LCD_COMMAND);
}

static void inline lcd_char(char val) {
    lcd_send_byte(val, LCD_CHARACTER);
}

void lcd_string(const char *s) {
    while (*s) {
        lcd_char(*s++);
    }
}

void lcd_init() {
    lcd_send_byte(0x03, LCD_COMMAND);
    lcd_send_byte(0x03, LCD_COMMAND);
    lcd_send_byte(0x03, LCD_COMMAND);
    lcd_send_byte(0x02, LCD_COMMAND);

    lcd_send_byte(LCD_ENTRYMODESET | LCD_ENTRYLEFT, LCD_COMMAND);
    lcd_send_byte(LCD_FUNCTIONSET | LCD_2LINE, LCD_COMMAND);
    lcd_send_byte(LCD_DISPLAYCONTROL | LCD_DISPLAYON, LCD_COMMAND);
    lcd_clear();
}


typedef enum {
    BULK_MODE,
    ABSORTION_MODE,
    FLOAT_MODE,
    SPIKE_MODE
} charging_mode_t;

// Saturador basico, se asegura que el PWM no sea ni negativo ni que se exceda del wrap
inline static uint16_t saturador(uint16_t wrap, int16_t level) {
    if(level > PWM_WRAP) {
        level = PWM_WRAP;
        return PWM_WRAP;
    }
    else if(level < 0) {
        level = 0;
        return 0;
    }
    return level;
}

float med_volt(float value){
    float prom = 0;
    for (int i = 0; i < 10; i++){
        float volt = BATTERY_ADC_RATIO * adc_read() * 3.3 / (1 << 12);
        prom = prom + volt;
        }
    return prom/10;
}

float med_current(float value){
    float prom = 0;
    for (int i = 0; i < 10; i++){
        float current = ((adc_read() * 3.3 / (1 << 12)) - 2.565) * (-10);
        prom = prom + current;
    }
    return prom/10;
}

float med_in(float value){
    float prom = 0;
    for (int i = 0; i < 10; i++){
        float volt = BATTERY_IN_RATIO * adc_read() * 3.3 / (1 << 12);
        prom = prom + volt;
    }
    if (prom < 5){
        prom = 0;
    }
    return prom/10;
}

int main() {
    #if !defined(i2c_default) || !defined(PICO_DEFAULT_I2C_SDA_PIN) || !defined(PICO_DEFAULT_I2C_SCL_PIN)
    #warning i2c/lcd_1602_i2c example requires a board with I2C pins
#else
    // This example will use I2C0 on the default SDA and SCL pins (4, 5 on a Pico)
    i2c_init(i2c_default, 100 * 1000);
    gpio_set_function(PICO_DEFAULT_I2C_SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(PICO_DEFAULT_I2C_SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(PICO_DEFAULT_I2C_SDA_PIN);
    gpio_pull_up(PICO_DEFAULT_I2C_SCL_PIN);
    // Make the I2C pins available to picotool
    bi_decl(bi_2pins_with_func(PICO_DEFAULT_I2C_SDA_PIN, PICO_DEFAULT_I2C_SCL_PIN, GPIO_FUNC_I2C));

    lcd_init();
#endif
    /* Inicializa el standard input/output de la pico */
    stdio_init_all();
    
    uint8_t pwm = 15;
    uint8_t slice = pwm_gpio_to_slice_num(pwm);
    int16_t pwm_level = PWM_WRAP / 2;

    // Se define el modo inicial como BULK
    charging_mode_t charging_mode = BULK_MODE;

    // Inicializacion del ADC
    adc_init();
    adc_gpio_init(ADC_GPIO_BATTERY);
    adc_gpio_init(ADC_CURRENT_BATTERY);
    adc_select_input(ADC_CHANNEL_BATTERY);

    uart_init(UART_ID, 2400);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    int __unused actual = uart_set_baudrate(UART_ID, BAUD_RATE);
    uart_set_hw_flow(UART_ID, false, false);
    uart_set_format(UART_ID, DATA_BITS, STOP_BITS, PARITY);
    uart_set_fifo_enabled(UART_ID, false);
    int UART_IRQ = UART_ID == uart0 ? UART0_IRQ : UART1_IRQ;
    irq_set_exclusive_handler(UART_IRQ, on_uart_rx);
    irq_set_enabled(UART_IRQ, true);
    uart_set_irq_enables(UART_ID, true, false);



    // Habilito GPIO como salida de PWM
    gpio_set_function(pwm, GPIO_FUNC_PWM);
    // Wrap para 33 KHz de PWM a 125 MHz de clock
    pwm_set_wrap(slice, PWM_WRAP);
    // 50% de ancho de pulso de partida
    pwm_set_gpio_level(pwm, pwm_level);
    // Habilitar PWM
    pwm_set_enabled(slice, true);
    // Boot inicial LCD
    lcd_clear();
    lcd_string("MPPT V 1.0   MODE:");
    lcd_set_cursor(1, 0);
    lcd_string("Vin: ");
    lcd_set_cursor(2, 0);
    lcd_string("Vo: ");
    lcd_set_cursor(3, 0);
    lcd_string("Io:       PWM:   %");

    add_alarm_in_ms(-1000, alarm_callback, NULL, false);

    while (true) {
        // Selecciono el canal de la tension y se lee y se convierte
        adc_select_input(ADC_CHANNEL_BATTERY);
        battery_voltage = med_volt(x);
        sprintf(str, "%.2f", battery_voltage);
        lcd_set_cursor(2, 4);
        lcd_string(str);
        // Selecciono el canal de la corriente y se lee y se convierte
        adc_select_input(ADC_CURRENT_CHANNEL_BATTERY);
        battery_current = med_current(x);
        sprintf(str, "%.2f", battery_current);
        lcd_set_cursor(3, 4);
        lcd_string(str);
        // Selecciono el canal de la entrada de tension, se lee y se convierte
        adc_select_input(ADC_CHANNEL_IN);
        battery_in = med_in(x);
        sprintf(str, "%.2f", battery_in);
        lcd_set_cursor(1, 4);
        lcd_string(str);

    ///////////////   MDOE VERIFICATION   ///////////////    
        if (charging_mode == BULK_MODE){
            if (battery_voltage > BULK_MAX_BATTERY_VOLTAGE) {
                    // Cambio modo de carga en caso de que corriente baje del umbral
                    charging_mode = ABSORTION_MODE;
                }
            else {
                lcd_set_cursor(1, 11);
                lcd_string("  BULK   ");
            }
        }
        if (charging_mode == ABSORTION_MODE){
            if (battery_current < ABSORTION_MIN_PANEL_CURRENT) {
                    // Cambio modo de carga en caso de que corriente baje del umbral
                    charging_mode = FLOAT_MODE;
                }
            else{
                lcd_set_cursor(1, 11);
                lcd_string("ABSORTION");
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
            else{
                lcd_set_cursor(1, 11);
                lcd_string("  FLOAT  ");
            }
        }

    ///////////////   END MDOE VERIFICATION   ///////////////   
    
    ///////////////   BULK   ///////////////
    
        if (charging_mode == BULK_MODE) {
            float error = (BULK_MAX_CURRENT_VOLTAGE - battery_current) * 25;
            if (battery_current > BULK_MAX_CURRENT_VOLTAGE) {
                pwm_level = pwm_level - (-1 * error * INTEGRAL_CONSTANT);
            }
            else {
                pwm_level += 1 * error * INTEGRAL_CONSTANT;
            }
            // Verifico que no exceda los limites
            pwm_level = saturador(PWM_WRAP, pwm_level);
            // Ajusto PWM
            pwm_set_gpio_level(pwm, pwm_level);

        }

    ///////////////   END BULK   ///////////////
    
    ///////////////   ABSORTION   ///////////////
        if (charging_mode == ABSORTION_MODE)  {
            float errorv = (ABSORTION_MAX_BATTERY_VOLTAGE - battery_voltage) * 6.849315;
            float errorc = (ABSORTION_MAX_PANEL_CURRENT - battery_current) * 25;
            if(battery_current > ABSORTION_MAX_PANEL_CURRENT) {
                pwm_level = pwm_level - (-1 * errorc * INTEGRAL_CONSTANT);
            }  
            else if(battery_voltage > ABSORTION_MAX_BATTERY_VOLTAGE) {
                // Incremento el duty en una unidad
                pwm_level += 1 * errorv * INTEGRAL_CONSTANT;
            }
            else {
                pwm_level = pwm_level - (-1 * errorv * INTEGRAL_CONSTANT);
            }
            // Verifico que no exceda los limites
            pwm_level = saturador(PWM_WRAP, pwm_level);
            // Ajusto PWM
            pwm_set_gpio_level(pwm, pwm_level);
        }
    ///////////////  END ABSORTION  ////////////////

    ///////////////  FLOAT  ////////////////
        if(charging_mode == FLOAT_MODE) {
            float error = (FLOAT_MAX_BATTERY_VOLTAGE - battery_voltage) * 7.24638;
            if (battery_voltage > FLOAT_MAX_BATTERY_VOLTAGE){
                pwm_level = pwm_level - (-1 * error * INTEGRAL_CONSTANT);
            }
            else {
                pwm_level += 1 * error * INTEGRAL_CONSTANT;
            }
            // Verifico que no exceda los limites
            pwm_level = saturador(PWM_WRAP, pwm_level);
            // Ajusto PWM
            pwm_set_gpio_level(pwm, pwm_level);
            
        }
    ///////////////  END FLOAT  ////////////////
        lcd_set_cursor(3, 14);
        sprintf(str, "%d", (int) (pwm_level * 0.0264061262));
        lcd_string(str);
    }
    return 0;
    
}