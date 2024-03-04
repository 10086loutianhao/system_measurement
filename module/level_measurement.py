#!/usr/bin/env python
# coding: utf-8

# In[281]:


import csv

#########    judge is there a rising or falling edge     #########

def DSview_posedge( previous_line, line, channel):
    if int(previous_line[channel]) == 0 and int(line[channel]) == 1:
        return 1
    else:
        return 0

def DSview_negedge( previous_line, line, channel):
    if int(previous_line[channel]) == 1 and int(line[channel]) == 0:
        return 1
    else:
        return 0

######   we use second channel as triggled channel  and sampling rate should be 1 M  ######

def process_csv_and_write(csvname, start_row, start_col, ws, ret_csv_dict):
    
    row_need_skip = []
    # 获取字典的键列表
    keys = list(ret_csv_dict.keys())
        
    with open(csvname) as f:
        csv_file = csv.reader(f) 
        count_1 = 0
        row = start_row
        col = start_col
        measure_allow = 0
        is_triggled = 0
        record_time = 0
        pulse_count = 0
        previous_line = [0, 0, 0]
        for line in csv_file:
            if count_1 < 6:
                count_1 += 1
                continue
            else:
                if count_1 == 6:   # this line is to update previous_line
                    count_1 += 1
                else:
                    if DSview_posedge(previous_line, line, 2) == 1:
                        is_triggled = 1

                    if (DSview_posedge(previous_line, line, 1) == 1) & (is_triggled == 1):
                        record_time = int(1000000 * float(line[0]))
                        measure_allow = 1
                    elif (DSview_negedge(previous_line, line, 1) == 1) & (is_triggled == 1):
                        if measure_allow == 1:
                            if pulse_count == len(keys):
                                row_need_skip.append(row)
                                pulse_count += 1
                            elif pulse_count < len(keys):
                                cell_num = int(1000000 * float(line[0])) - record_time
                                key = keys[pulse_count]
#                                 print("pulse_count = ", end="")
#                                 print(pulse_count)
#                                 print("row = ", end="")
#                                 print(row)
#                                 print("col + ret_csv_dict[key] = ", end="")
#                                 print(col + ret_csv_dict[key])
#                                 print("cell_num = ", end="")
#                                 print(cell_num)
                                ws.cell(row, col + ret_csv_dict[key], cell_num)
                                measure_allow = 0
                                pulse_count += 1   

                    if DSview_negedge(previous_line, line, 2) == 1 & is_triggled == 1:
                        is_triggled = 0
                        if pulse_count == len(keys):
                            pulse_count = 0
                        else :
                            raise SystemExit("pulse_count Error!")
                        row += 1
                previous_line = line
                
    print("process csv data ok! csv data have been recorded in ws, and bad data have been discarded") 
#     print("row_need_skip = ", end="")
#     print(row_need_skip)
    return row_need_skip

def find_max_value_in_csv_sublist(start_row, end_row, start_col, ws, ret_csv_dict, row_need_skip):
    
    csv_maximum = [0] * len(ret_csv_dict)
    csv_minimum = [0] * len(ret_csv_dict)

    col = start_col
    
    # 获取字典的键列表
    keys = list(ret_csv_dict.keys())

    for row_num in range(start_row, end_row):
        if row_num in row_need_skip:
            if row_num == start_row:
                start_row += 1
            continue
            
        for item in range(len(ret_csv_dict)):
            key = keys[item]
            if row_num == start_row:
                csv_maximum[item] = ws.cell(row_num, col + ret_csv_dict[key]).value
                csv_minimum[item] = ws.cell(row_num, col + ret_csv_dict[key]).value
            if row_num > start_row:
                if csv_maximum[item] < ws.cell(row_num, col + ret_csv_dict[key]).value:
                    csv_maximum[item] = ws.cell(row_num, col + ret_csv_dict[key]).value
                if csv_minimum[item] > ws.cell(row_num, col + ret_csv_dict[key]).value:
                    csv_minimum[item] = ws.cell(row_num, col + ret_csv_dict[key]).value
                    
    print("csv data maximum and minimum have been recorded in dict and will be utilized for cartography")                  
    return {'csv_maximum': csv_maximum, 'csv_minimum': csv_minimum}
