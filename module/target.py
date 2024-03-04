#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# set Target chip 、IDF_PATH 、 Target uart port
import subprocess
import serial.tools.list_ports
import os

def target_init():
    IDF_PATH = os.path.abspath(os.path.join(os.getcwd(), '..', 'esp-idf'))
    set_target_method = ''
    preview_flag = input("y or n --preview:")
    if (preview_flag == 'y'):
        set_target_method = 'idf.py --preview set-target '
    elif (preview_flag == 'n'):
        set_target_method = 'idf.py set-target '
    else:
        raise SystemExit("preview_flag Error!")
    CHIP_TARGET = input("Select CHIP_TARGET:")
    val = input("Select Port: /dev/ttyUSB")
    
    EXAMPLE_PATH = os.path.abspath(os.path.join(os.getcwd(), '..', 'auto_light_sleep'))
    subprocess.call([' cd  '+ IDF_PATH + ' ;  ./install.sh ; . ./export.sh ; \
                    cd ' + EXAMPLE_PATH + ' ; ' + set_target_method + CHIP_TARGET ], shell=True)
    ports = serial.tools.list_ports.comports()
    portsList = []

    for onePort in ports:
        portsList.append(str(onePort))
        print(str(onePort))

    target_port = ''

    for x in range(0,len(portsList)):
        if portsList[x].startswith("/dev/ttyUSB" + str(val)):
            portVar = "/dev/ttyUSB" + str(val)
            print(portVar)
            target_port = portVar
            
    return [IDF_PATH, EXAMPLE_PATH, target_port]

