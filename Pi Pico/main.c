#include "hardware/pwm.h"
#include "hardware/adc.h"
void main() {
uint pwm = 22;
uint slice_num = pwm_gpio_to_slice_num(22);

gpio_set_function(pwm, GPIO_FUNC_PWM);
pwm_set_wrap(slice_num, 3787);
pwm_set_gpio_level(pwm, 1893);
pwm_set_enabled(slice_num, true);
while 1;
}