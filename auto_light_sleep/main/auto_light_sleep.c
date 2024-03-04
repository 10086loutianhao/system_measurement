/*
 * SPDX-FileCopyrightText: 2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Unlicense OR CC0-1.0
 */
/* Power save Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/

/*
   this example shows how to use power save mode
   set a router or a AP using the same SSID&PASSWORD as configuration of this example.
   start esp32 and when it connected to AP it will enter power save mode
*/
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_event.h"
#include "esp_pm.h"
#include "soc/lp_aon_reg.h"
#include "soc/lpperi_reg.h"
#include "soc/gpio_reg.h"
#include "esp_private/sleep_event.h"
#if CONFIG_IDF_TARGET_ESP32C6
#include "soc/lp_io_reg.h"
#include "soc/lp_clkrst_reg.h"
#endif
#include "driver/gpio.h"
#include "soc/io_mux_reg.h"
#include "esp_attr.h"
#include "esp_sleep.h"

#if CONFIG_IDF_TARGET_ESP32H2
void LP_DEBUG_MATRIX_CFG(uint32_t signal_sel, uint32_t gpio_num)
{
    //internal LP IO 0~7 ==> external GPIO 7~14

    /**
     * No.      Name
     * 23       LP_ANA_WAIT
     * 20       LP_XTAL_WAIT
     * 7        HP_ANA_WAIT
     * 8        HP_PD_DIG
     * 9        HP_XTAL_WAIT
     * 10       SYS_CLK_SEL
     * 11       BACK_UP
     * 12       ICG
     * 13       PAUSE
     * 52       POCLK_OSC32K RC32K
     * 53       40M XTAL
     * 55       POCLK_SOSC 150khz
     * 56       POCLK_XTAL32K
     * 66       task_hp_clk_power_ack
     * 71       task_pd_dig_ack
     * 26       PMU HP MODEM
     * 28       PMU HP ACTIVE
     * 27       HP_SLEEP
     * 24       LP_SLEEP
     * 21       LP_CK_SWITCH
     * 45       REGDMA work
     * 59       PMU SOC wakeup
     * 92       Modem SOC Wakeup
     * 93       Modem Sleep REQ
     * 94       RF flag
     * 95       RX Frame
     */

    uint32_t gpio_num_tmp;
    if (gpio_num>=6){
        gpio_num_tmp = gpio_num - 5;
    }
    else{
        gpio_num_tmp = gpio_num;
    }
    SET_PERI_REG_BITS(LP_AON_GPIO_MUX_REG, LP_AON_GPIO_MUX_SEL, 0xff, LP_AON_GPIO_MUX_SEL_S);
    if (gpio_num_tmp <= 3){
        SET_PERI_REG_BITS(LPPERI_DEBUG_SEL0_REG, LPPERI_DEBUG_SEL0, signal_sel, LPPERI_DEBUG_SEL0_S + gpio_num_tmp * 7);
    }
    else{
        SET_PERI_REG_BITS(LPPERI_DEBUG_SEL1_REG, LPPERI_DEBUG_SEL4, signal_sel, LPPERI_DEBUG_SEL4_S);
    }
}
#endif

#if CONFIG_IDF_TARGET_ESP32C6
static void dbug_pmu_signal_io_init(void)
{
    /**
     * No.      Name
     * 7        HP_PD_ANA
     * 8        HP_PD_DIG
     * 22       LP_PD_ANA
     * 9        HP_CLK_POWER
     * 19       LP_CLK_POWER
     * 26       PMU HP MODEM
     * 28       PMU HP ACTIVE
     * 45       REGDMA work
     * 59       PMU SOC wakeup
     * 92       Modem SOC Wakeup
     * 93       Modem Sleep REQ
     * 94       RF flag
     * 95       RX Frame
     */
    static struct { uint32_t sig: 16, io: 16; } mapTab[] = {
// !CONFIG_RTC_CLK_SRC_EXT_CRYS
#if 0
        [0] = { .sig = 26,      .io = 0 },
        [1] = { .sig = 28,      .io = 1 },
#else
        [0] = { .sig = 19,      .io = 5 },
        [1] = { .sig = 11,      .io = 6 },
#endif
        [2] = { .sig = 7,      .io = 2 },
        [3] = { .sig = 22,      .io = 3 },
        [4] = { .sig = 8,      .io = 4 }
    };
    /* map PMU MODEM signal to GPIO0 */
    *(volatile uint32_t *)LP_AON_GPIO_MUX_REG |= BIT(mapTab[0].io);
    *(volatile uint32_t *)LP_IO_DEBUG_SEL0_REG |= (mapTab[0].sig & 0x7f);
// !CONFIG_RTC_CLK_SRC_EXT_CRYS
#if 0
    *(volatile uint32_t *)LP_IO_GPIO0_REG |= ((2 & 0x7) << 12);
#else
    *(volatile uint32_t *)LP_IO_GPIO5_REG |= ((2 & 0x7) << 12);
#endif
    *(volatile uint32_t *)LP_CLKRST_LP_CLK_PO_EN_REG = 0xffffffff;

    /* map PMU ACTIVE signal to GPIO1 */
    *(volatile uint32_t *)LP_AON_GPIO_MUX_REG |= BIT(mapTab[1].io);
    *(volatile uint32_t *)LP_IO_DEBUG_SEL0_REG |= (mapTab[1].sig & 0x7f) << 7;
// !CONFIG_RTC_CLK_SRC_EXT_CRYS
#if 0
    *(volatile uint32_t *)LP_IO_GPIO1_REG |= ((2 & 0x7) << 12);
#else
    *(volatile uint32_t *)LP_IO_GPIO6_REG |= ((2 & 0x7) << 12);
#endif
    *(volatile uint32_t *)LP_CLKRST_LP_CLK_PO_EN_REG = 0xffffffff;

    /* map PMU SOC wakeup signal to GPIO2 */
    *(volatile uint32_t *)LP_AON_GPIO_MUX_REG |= BIT(mapTab[2].io);
    *(volatile uint32_t *)LP_IO_DEBUG_SEL0_REG |= (mapTab[2].sig & 0x7f) << 14;
    *(volatile uint32_t *)LP_IO_GPIO2_REG |= ((2 & 0x7) << 12);
    *(volatile uint32_t *)LP_CLKRST_LP_CLK_PO_EN_REG = 0xffffffff;

    /* map REGDMA work signal to GPIO3 */
    *(volatile uint32_t *)LP_AON_GPIO_MUX_REG |= BIT(mapTab[3].io);
    *(volatile uint32_t *)LP_IO_DEBUG_SEL0_REG |= (mapTab[3].sig & 0x7f) << 21;
    *(volatile uint32_t *)LP_IO_GPIO3_REG |= ((2 & 0x7) << 12);
    *(volatile uint32_t *)LP_CLKRST_LP_CLK_PO_EN_REG = 0xffffffff;

    /* map Modem SOC wakeup signal to GPIO4 */
    *(volatile uint32_t *)LP_AON_GPIO_MUX_REG |= BIT(mapTab[4].io);
    *(volatile uint32_t *)LP_IO_DEBUG_SEL1_REG |= (mapTab[4].sig & 0x7f);
    *(volatile uint32_t *)LP_IO_GPIO4_REG |= ((2 & 0x7) << 12);
    *(volatile uint32_t *)LP_CLKRST_LP_CLK_PO_EN_REG = 0xffffffff;

    esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH,ESP_PD_OPTION_ON);
}
#endif

uint32_t light_sleep_loop;
uint32_t overhead_in[3000], overhead_out[3000];
#define loop_num 100

extern void esp_sleep_register_test_event_callbacks(void);
extern void esp_sleep_register_test_pm_callbacks(void);
// *(uint32_t *) GPIO_ENABLE_REG = 1 << 4;
// *(uint32_t *) GPIO_ENABLE_W1TS_REG = 1 << 4;
// PIN_FUNC_SELECT(IO_MUX_GPIO4_REG, 1);
// *(uint32_t *) GPIO_OUT_W1TS_REG = 1 << 4;

void app_main(void)
{
#if CONFIG_ESP_SLEEP_EVENT_CALLBACKS
    esp_sleep_register_test_event_callbacks();
#endif
#if CONFIG_PM_LIGHT_SLEEP_CALLBACKS
    esp_sleep_register_test_pm_callbacks();
#endif
    // dbug_pmu_signal_io_init();

#if CONFIG_PM_ENABLE
    // Configure dynamic frequency scaling:
    // maximum and minimum frequencies are set in sdkconfig,
    // automatic light sleep is enabled if tickless idle support is enabled.
    esp_pm_config_t pm_config = {
            .max_freq_mhz = CONFIG_EXAMPLE_MAX_CPU_FREQ_MHZ,
            .min_freq_mhz = CONFIG_EXAMPLE_MIN_CPU_FREQ_MHZ,
#if CONFIG_FREERTOS_USE_TICKLESS_IDLE
            .light_sleep_enable = true
#endif
    };
    ESP_ERROR_CHECK( esp_pm_configure(&pm_config) );
#endif // CONFIG_PM_ENABLE

    // LP_DEBUG_MATRIX_CFG(23, 1);
    // LP_DEBUG_MATRIX_CFG(20, 2);
    // LP_DEBUG_MATRIX_CFG(24, 3);
    // LP_DEBUG_MATRIX_CFG(27, 4);

    uint32_t delay_time = 1000 *1;
    int i = 1;
    while (light_sleep_loop < loop_num + 1) {
        printf("Restarting in %d seconds...\n", i++);
        vTaskDelay(delay_time / portTICK_PERIOD_MS);
    }
    esp_rom_printf("start_to_send_data\n");
    for (int i = 1; i < loop_num + 1; i++){
        esp_rom_printf("%ld, %ld\n", overhead_out[i], overhead_in[i]);
    }
    esp_rom_printf("stop_to_send_data\n");

    while(1);
}
