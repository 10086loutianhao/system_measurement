#!/usr/bin/env python
# coding: utf-8

# In[23]:


# set DFS , PD flash , Config flash SPI , Put sleep relative code in ram 
import subprocess
import os

def set_menucofig_command(DFS_min, DFS_max, PD_flash_flag, RTC_source, IDF_PATH):
    EXAMPLE_PATH = os.path.abspath(os.path.join(os.getcwd(), '..', 'auto_light_sleep'))
    menucofig_command = 'cd '+ EXAMPLE_PATH + '; \
                sed -i \'s/.*CONFIG_ESPTOOLPY_FLASHMODE_QIO.*/CONFIG_ESPTOOLPY_FLASHMODE_QIO=y/\' sdkconfig; \
                sed -i \'s/.*CONFIG_ESPTOOLPY_FLASHMODE_QOUT.*/# CONFIG_ESPTOOLPY_FLASHMODE_QOUT is not set/\' sdkconfig; \
                sed -i \'s/.*CONFIG_ESPTOOLPY_FLASHMODE_DIO.*/# CONFIG_ESPTOOLPY_FLASHMODE_DIO is not set/\' sdkconfig; \
                sed -i \'s/.*CONFIG_ESPTOOLPY_FLASHMODE_DOUT.*/# CONFIG_ESPTOOLPY_FLASHMODE_DOUT is not set/\' sdkconfig; \
                \
                sed -i \'s/# CONFIG_ESPTOOLPY_FLASHFREQ_64M is not set/CONFIG_ESPTOOLPY_FLASHFREQ_64M=y/\' sdkconfig; \
                sed -i \'s/.*CONFIG_ESPTOOLPY_FLASHFREQ_32M.*/# CONFIG_ESPTOOLPY_FLASHFREQ_32M is not set/\' sdkconfig; \
                sed -i \'s/.*CONFIG_ESPTOOLPY_FLASHFREQ_16M.*/# CONFIG_ESPTOOLPY_FLASHFREQ_16M is not set/\' sdkconfig; \
                sed -i \'s/CONFIG_ESPTOOLPY_FLASHFREQ=/CONFIG_ESPTOOLPY_FLASHFREQ="64m"/\' sdkconfig; \
                \
                sed -i \'s/.*CONFIG_PM_SLP_IRAM_OPT.*/CONFIG_PM_SLP_IRAM_OPT=y/\' sdkconfig; \
                sed -i \'s/.*CONFIG_ESP_SLEEP_EVENT_CALLBACKS.*/CONFIG_ESP_SLEEP_EVENT_CALLBACKS=y/\' sdkconfig; \
                sed -i \'s/.*CONFIG_PM_RTOS_IDLE_OPT.*/CONFIG_PM_RTOS_IDLE_OPT=y/\' sdkconfig; '
 
    menucofig_command += 'sed -i \'s/.*CONFIG_EXAMPLE_MIN_CPU_FREQ.*/CONFIG_EXAMPLE_MIN_CPU_FREQ_'+ str(DFS_min) + 'M=y' + '/' + '\' sdkconfig;'
    
    menucofig_command += 'sed -i \'s/.*CONFIG_EXAMPLE_MAX_CPU_FREQ.*/CONFIG_EXAMPLE_MAX_CPU_FREQ_'+ str(DFS_max) + 'M=y' + '/' + '\' sdkconfig;'
    
    if PD_flash_flag == 'PD_flash':
        menucofig_command += 'sed -i \'s/.*CONFIG_ESP_SLEEP_POWER_DOWN_FLASH.*/CONFIG_ESP_SLEEP_POWER_DOWN_FLASH=y/\' sdkconfig;'
    elif PD_flash_flag == 'PU_flash':
        menucofig_command += 'sed -i \'s/.*CONFIG_ESP_SLEEP_POWER_DOWN_FLASH.*/# CONFIG_ESP_SLEEP_POWER_DOWN_FLASH is not set/\' sdkconfig;'
    else:
        raise SystemExit("Parameter Error!")
    if RTC_source == 'internal_136k_Rc':
        menucofig_command += 'sed -i \'s/# CONFIG_RTC_CLK_SRC_INT_RC is not set/CONFIG_RTC_CLK_SRC_INT_RC=y/\' sdkconfig; \
                    sed -i \'s/.*CONFIG_RTC_CLK_SRC_EXT_CRYS.*/# CONFIG_RTC_CLK_SRC_EXT_CRYS is not set/\' sdkconfig; \
                    sed -i \'s/.*CONFIG_RTC_CLK_SRC_INT_RC32K.*/# CONFIG_RTC_CLK_SRC_INT_RC32K is not set/\' sdkconfig;'
    elif RTC_source == 'internal_32k_Rc':
        menucofig_command += 'sed -i \'s/CONFIG_RTC_CLK_SRC_INT_RC=y/# CONFIG_RTC_CLK_SRC_INT_RC is not set/\' sdkconfig; \
                    sed -i \'s/.*CONFIG_RTC_CLK_SRC_EXT_CRYS.*/# CONFIG_RTC_CLK_SRC_EXT_CRYS is not set/\' sdkconfig; \
                    sed -i \'s/.*CONFIG_RTC_CLK_SRC_INT_RC32K.*/CONFIG_RTC_CLK_SRC_INT_RC32K=y/\' sdkconfig;'
    elif RTC_source == 'external_32k_crystal':
        menucofig_command += 'sed -i \'s/CONFIG_RTC_CLK_SRC_INT_RC=y/# CONFIG_RTC_CLK_SRC_INT_RC is not set/\' sdkconfig; \
                    sed -i \'s/.*CONFIG_RTC_CLK_SRC_EXT_CRYS.*/CONFIG_RTC_CLK_SRC_EXT_CRYS=y/\' sdkconfig; \
                    sed -i \'s/.*CONFIG_RTC_CLK_SRC_INT_RC32K.*/CONFIG_RTC_CLK_SRC_INT_RC32K is not set/\' sdkconfig;'
    
    else:
        raise SystemExit("Parameter Error!")
        
    subprocess.call([menucofig_command], shell=True)
    return

