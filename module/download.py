#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# set sleep time and download flash
import subprocess
from serial_contorl import serial_rst_chip_to_download
import time

def change_time_value_and_download(times, IDF_PATH, EXAMPLE_PATH, target_port, baud = 115200):
    
    oneshot_timer_command = ' cd ' + IDF_PATH + ' ; . ./export.sh ; \
                cd '+ EXAMPLE_PATH + ' ; cd main;'
    oneshot_timer_command += 'sed -i \'s/.*delay_time =.*/    uint32_t delay_time = 1000 *'+ str(times) + ';/\' auto_light_sleep.c;'  
    oneshot_timer_command += 'cd .. ; idf.py flash -p ' + target_port + ';'
    
    download_out = subprocess.call([oneshot_timer_command], shell=True)
    if download_out != 0:
        raise SystemExit("Download Error!")
    
    time.sleep(0.5)
    serial_rst_chip_to_download(target_port, baud)
    return
