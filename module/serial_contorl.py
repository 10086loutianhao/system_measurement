#!/usr/bin/env python
# coding: utf-8

# In[272]:


# serial contorl
import time
import serial
from openpyxl import Workbook

def serial_rst_chip_to_boot(target_port, baud = 115200):
    
    serialInst = serial.Serial()
    serialInst.baudrate = baud
    serialInst.port = target_port
    serialInst.rts = False
    serialInst.dtr = False
    serialInst.open()
    serialInst.close()

def serial_rst_chip_to_download(target_port, baud = 115200):
    
    serialInst = serial.Serial()
    serialInst.baudrate = baud
    serialInst.port = target_port
    serialInst.rts = True
    serialInst.dtr = False
    serialInst.open()
    serialInst.close()
    time.sleep(0.5)
    serialInst.rts = False
    serialInst.dtr = True
    serialInst.open()
    serialInst.close()
    
def serial_process_data(target_port, ws, start_row, start_col, ret_serial_dict, baud = 115200):
        
    serialInst = serial.Serial()
    serialInst.baudrate = baud
    serialInst.port = target_port
    serialInst.open()
    
    # 获取字典的键列表
    keys = list(ret_serial_dict.keys())
    
    row = start_row    
    col = start_col
    print_allow = 0
    process_uart_data = 0
    while not process_uart_data:
        if serialInst.in_waiting:
            packet = serialInst.readline()
            if packet.decode('utf').rstrip('\n')[-18:-1] == 'stop_to_send_data':
                process_uart_data = 1
                print_allow = 0
            if print_allow == 1:
                #print(packet.decode('utf').rstrip('\n'))
                for num in range(len(ret_serial_dict)):
                    cell_num = int(str(packet.decode('utf').rstrip('\n')[-19:-1]).split(',')[num])
                    key = keys[num]
#                     print("row = ", end="")
#                     print(row)
#                     print("col + ret_serial_dict[key] = ", end="")
#                     print(col + ret_serial_dict[key])
#                     print("cell_num = ", end="")
#                     print(cell_num)
                    ws.cell(row, col + ret_serial_dict[key], cell_num)
                row = row + 1
            if packet.decode('utf').rstrip('\n')[-19:-1] == 'start_to_send_data':
                print_allow = 1

    serialInst.close()
    end_row = row
    print("process serial data ok! serial data have been recorded in ws")
#     print("end_row = ", end="")
#     print(end_row)
    return end_row

