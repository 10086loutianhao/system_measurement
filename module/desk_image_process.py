#!/usr/bin/env python
# coding: utf-8

# In[1]:

#######   Grab the part of the screen to make sure sucessfully export csv   #######
import pyscreenshot as ImageGrab
import numpy as np
import time

def wait_export_csv(input_pos):
    ok_pos_x = input_pos[6]
    ok_pos_y = input_pos[7]
    im_1 = ImageGrab.grab(bbox=(ok_pos_x - 10, ok_pos_y - 10, ok_pos_x + 10, ok_pos_y + 10))  # X1,Y1,X2,Y2
    im_1_np = np.array(im_1)

    while True:
        time.sleep(0.5)
        im_2 = ImageGrab.grab(bbox=(ok_pos_x - 10, ok_pos_y - 10, ok_pos_x + 10, ok_pos_y + 10))  # X1,Y1,X2,Y2
        im_2_np = np.array(im_2)
        if sum(sum(sum(im_1_np - im_2_np))) != 0:
            print("export csv ok!")
            break






