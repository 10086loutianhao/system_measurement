#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# mouse DSview contorl
import time
import pyautogui

def pos_init():
    
    input("Press Enter to get start pos...")
    start_pos_x = pyautogui.position().x
    start_pos_y = pyautogui.position().y
    input("Press Enter to get file pos...")
    file_pos_x = pyautogui.position().x
    file_pos_y = pyautogui.position().y
    input("Press Enter to get change pos...")
    change_pos_x = pyautogui.position().x
    change_pos_y = pyautogui.position().y
    input("Press Enter to get ok pos...")
    ok_pos_x = pyautogui.position().x
    ok_pos_y = pyautogui.position().y
    input("Please press Cancel key to continue...")
    
    return [start_pos_x, start_pos_y, file_pos_x, file_pos_y, change_pos_x, change_pos_y, ok_pos_x, ok_pos_y]

def click_start(input_pos):
    
    start_pos_x = input_pos[0]
    start_pos_y = input_pos[1]
    pyautogui.moveTo(start_pos_x, start_pos_y, duration = 3)
    pyautogui.click(start_pos_x, start_pos_y)
    print("DSview measure start")

def click_stop(input_pos):
    
    stop_pos_x = input_pos[0]
    stop_pos_y = input_pos[1]
    pyautogui.moveTo(stop_pos_x, stop_pos_y, duration = 3)
    pyautogui.click(stop_pos_x, stop_pos_y)
    print("DSview measure stop")

def click_file(input_pos):
    
    file_pos_x = input_pos[2]
    file_pos_y = input_pos[3]
    pyautogui.moveTo(file_pos_x, file_pos_y, duration = 1)
    pyautogui.click(file_pos_x, file_pos_y)
    pyautogui.moveTo(file_pos_x, file_pos_y + 116, duration = 1)
    pyautogui.click(file_pos_x, file_pos_y + 116)
    
def click_change(input_pos):
    
    change_pos_x = input_pos[4]
    change_pos_y = input_pos[5]
    pyautogui.moveTo(change_pos_x, change_pos_y, duration = 1)
    pyautogui.click(change_pos_x, change_pos_y)

def click_ok_and_leave(input_pos):
    
    ok_pos_x = input_pos[6]
    ok_pos_y = input_pos[7]
    pyautogui.moveTo(ok_pos_x, ok_pos_y, duration = 1)
    pyautogui.click(ok_pos_x, ok_pos_y)
    pyautogui.moveTo(ok_pos_x, ok_pos_y + 100, duration = 0.1)

