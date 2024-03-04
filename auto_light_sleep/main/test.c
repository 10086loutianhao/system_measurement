/*
 * SPDX-FileCopyrightText: 2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Unlicense OR CC0-1.0
 */
#include <stdbool.h>
#include "esp_attr.h"
#include "soc/gpio_reg.h"
#include "driver/gpio.h"
#include "esp_sleep.h"
#include "esp_private/sleep_event.h"
#include "esp_pm.h"

#if CONFIG_IDF_TARGET_ESP32C6
#define DBUG_GPIO_DEFAULT()   { GPIO_NUM_2, GPIO_NUM_3, GPIO_NUM_4, GPIO_NUM_5, GPIO_NUM_6 }
#elif CONFIG_IDF_TARGET_ESP32H2
#define DBUG_GPIO_DEFAULT()   { GPIO_NUM_10, GPIO_NUM_11 }
#endif

#define SLEEP_EVENT_HW_START_TO_WORK 0

/* To re-write the weak symbol is defined in
 * $IDF_PATH/components/esp_hw_support/sleep_cpu_asm.S */
IRAM_ATTR void rv_core_critical_regs_restore(void)
{
    __asm__ __volatile__ (".extern __rv_core_critical_regs_restore");
    __asm__ __volatile__ ("tail __rv_core_critical_regs_restore");
}

static inline gpio_config_t s_init_io(gpio_num_t num)
{
    gpio_config_t io_conf;
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pin_bit_mask = (1ULL << num);
    io_conf.pull_down_en = 0;
    io_conf.pull_up_en = 0;
    return io_conf;
}

void dbug_gpio_init(void)
{
    const static int iolsts[] = DBUG_GPIO_DEFAULT();

    for (int i = 0; i < sizeof(iolsts) / sizeof(iolsts[0]); i++) {
        gpio_config_t iocfg = s_init_io(iolsts[i]);
        gpio_config(&iocfg);
    }
}

extern uint32_t light_sleep_loop;
extern uint32_t overhead_in[], overhead_out[];

IRAM_ATTR esp_err_t debug_gpio_pull_up(void *gpio_param, void *extern_arg)
{
#if CONFIG_IDF_TARGET_ESP32C6
    REG_WRITE(GPIO_OUT_W1TS_REG, BIT(GPIO_NUM_2));
#elif CONFIG_IDF_TARGET_ESP32H2
    REG_WRITE(GPIO_OUT_W1TS_REG, BIT(GPIO_NUM_10));
#endif
    return ESP_OK;
}

IRAM_ATTR esp_err_t debug_gpio_pull_down(void *gpio_param, void *extern_arg)
{
#if CONFIG_IDF_TARGET_ESP32C6
    REG_WRITE(GPIO_OUT_W1TC_REG, BIT(GPIO_NUM_2));
#elif CONFIG_IDF_TARGET_ESP32H2
    REG_WRITE(GPIO_OUT_W1TC_REG, BIT(GPIO_NUM_10));
#endif
    return ESP_OK;
}

IRAM_ATTR esp_err_t triggle_gpio_pull_up(void *gpio_param, void *extern_arg)
{
#if CONFIG_IDF_TARGET_ESP32C6
    REG_WRITE(GPIO_OUT_W1TS_REG, BIT(GPIO_NUM_3));
#elif CONFIG_IDF_TARGET_ESP32H2
    REG_WRITE(GPIO_OUT_W1TS_REG, BIT(GPIO_NUM_11));
#endif
    return ESP_OK;
}

IRAM_ATTR esp_err_t triggle_gpio_pull_down(void *gpio_param, void *extern_arg)
{
#if CONFIG_IDF_TARGET_ESP32C6
    REG_WRITE(GPIO_OUT_W1TC_REG, BIT(GPIO_NUM_3));
#elif CONFIG_IDF_TARGET_ESP32H2
    REG_WRITE(GPIO_OUT_W1TC_REG, BIT(GPIO_NUM_11));
#endif
    return ESP_OK;
}

IRAM_ATTR esp_err_t light_sleep_loop_increase(void *gpio_param, void *extern_arg)
{
    light_sleep_loop ++;
    return ESP_OK;
}

IRAM_ATTR esp_err_t light_sleep_record_overhead(void *gpio_param, void *extern_arg)
{
    overhead_in[light_sleep_loop] = ((uint32_t *)extern_arg)[0];
    overhead_out[light_sleep_loop] = ((uint32_t *)extern_arg)[1];
    return ESP_OK;
}

IRAM_ATTR esp_err_t delay_some_time(void *gpio_param, void *extern_arg)
{
    for (int i =0; i < 15; i++) {
        asm volatile ( "nop" );
    }
    return ESP_OK;
}

#if CONFIG_ESP_SLEEP_EVENT_CALLBACKS
void esp_sleep_register_test_event_callbacks()
{
    dbug_gpio_init();

    esp_sleep_event_cb_config_t event_cb_conf = {
        .cb = triggle_gpio_pull_up,
        .user_arg = NULL,
        .prior = 0,
    };
    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_HW_START_TO_WORK, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_down;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 0;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_SW_CPU_TO_MEM_END, &event_cb_conf) );

    event_cb_conf.cb = triggle_gpio_pull_down;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 1;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_SW_CPU_TO_MEM_END, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_up;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 1;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_HW_START_TO_WORK, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_down;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 0;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_HW_EXIT_SLEEP, &event_cb_conf) );

    event_cb_conf.cb = delay_some_time;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 1;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_HW_EXIT_SLEEP, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_up;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 2;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_HW_EXIT_SLEEP, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_down;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 0;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_SW_CLK_READY, &event_cb_conf) );

    event_cb_conf.cb = delay_some_time;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 1;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_SW_CLK_READY, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_up;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 2;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_SW_CLK_READY, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_down;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 0;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_SW_EXIT_SLEEP, &event_cb_conf) );

    event_cb_conf.cb = light_sleep_record_overhead;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 1;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_SW_EXIT_SLEEP, &event_cb_conf) );

    event_cb_conf.cb = light_sleep_loop_increase;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 2;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_SW_EXIT_SLEEP, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_up;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 0;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_SW_GOTO_SLEEP, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_down;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 0;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_HW_TIME_START, &event_cb_conf) );

    event_cb_conf.cb = delay_some_time;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 1;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_HW_TIME_START, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_up;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 2;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_HW_TIME_START, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_down;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 0;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_HW_GOTO_SLEEP, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_up;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 0;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_SW_CPU_TO_MEM_START, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_up;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 0;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_HW_BBPLL_EN_START, &event_cb_conf) );

    event_cb_conf.cb = debug_gpio_pull_down;
    event_cb_conf.user_arg = NULL;
    event_cb_conf.prior = 0;

    ESP_ERROR_CHECK( esp_sleep_register_event_callback(SLEEP_EVENT_HW_BBPLL_EN_STOP, &event_cb_conf) );
}

IRAM_ATTR void rtc_clk_set_cpu_switch_to_bbpll(int event_id)
{
    esp_sleep_execute_event_callbacks(event_id, (void *)0);
}
#endif

IRAM_ATTR void rv_core_test_c_handler(void)
{
    esp_sleep_execute_event_callbacks(SLEEP_EVENT_HW_START_TO_WORK, (void *)0);
}

#if CONFIG_PM_LIGHT_SLEEP_CALLBACKS
void esp_sleep_register_test_pm_callbacks()
{
    dbug_gpio_init();

    esp_pm_sleep_cbs_register_config_t cbs_conf1 = {
        .enter_cb = NULL,
        .enter_cb_user_arg = NULL,
        .enter_cb_prior = 0,
        .exit_cb = triggle_gpio_pull_up,
        .exit_cb_user_arg = NULL,
        .exit_cb_prior = 0,
    };
    ESP_ERROR_CHECK( esp_pm_light_sleep_register_cbs(&cbs_conf1) );

    esp_pm_sleep_cbs_register_config_t cbs_conf2 = {
        .enter_cb = NULL,
        .enter_cb_user_arg = NULL,
        .enter_cb_prior = 0,
        .exit_cb = triggle_gpio_pull_down,
        .exit_cb_user_arg = NULL,
        .exit_cb_prior = 0,
    };
    ESP_ERROR_CHECK( esp_pm_light_sleep_register_cbs(&cbs_conf2) );
}
#endif
