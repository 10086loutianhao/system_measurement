#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# use for chart

from pyecharts.charts import *
from pyecharts.components import Table
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
import random
import datetime
from pyecharts.globals import CurrentConfig
from pyecharts_snapshot.main import make_a_snapshot
from pyecharts.charts import Line
from pyecharts.globals import CurrentConfig
CurrentConfig.ONLINE_HOST = "https://cdn.kesci.com/lib/pyecharts_assets/"

def draw_html_for_results_pyecharts(dict_list, dev_str_mapping, \
                          DFS_min_list, DFS_max_list, RTC_source_list, times_list, PD_flash_flag_list, title_prefix):
       
    # 获取字典的键列表
    keys_list = list(dev_str_mapping.keys())
    
    dev_max_str_list = dev_str_mapping.get(keys_list[0], [])
    dev_min_str_list = dev_str_mapping.get(keys_list[1], [])
    
    for DFS_min in DFS_min_list:
        for DFS_max in DFS_max_list:
            for RTC_source in RTC_source_list:
                for times in times_list:
                    for PD_flash_flag in PD_flash_flag_list:
                        num_dev_sublists = len(dev_max_str_list)
                        dev_max = [[] for _ in range(num_dev_sublists)]
                        dev_min = [[] for _ in range(num_dev_sublists)]

                        for obj in dict_list:
                            if obj['dfs_min'] == DFS_min and obj['dfs_max'] == DFS_max and obj['PD_flash_flag'] == PD_flash_flag:
                                if obj['times'] == times:
                                    for i in range(num_dev_sublists):
                                        dev_max[i].append(obj[keys_list[0]][i])
                                        dev_min[i].append(obj[keys_list[1]][i])

                        title_str = "DFS_" + str(DFS_min) + "~" + str(DFS_max) + "_" + str(times) + "*1s_" + PD_flash_flag
                        line = (Line()
                                .add_xaxis(RTC_source_list)
                                .set_global_opts(
                                    title_opts=opts.TitleOpts(title=title_str, pos_top="25", pos_left="center"),
                                    xaxis_opts=opts.AxisOpts(name="RTC source"),
                                    yaxis_opts=opts.AxisOpts(name="偏差(us)"),
                                    legend_opts=opts.LegendOpts(pos_left='center', pos_top='bottom', item_gap=20, \
                                                                orient='horizontal', selected_mode='multiple', item_height=15)
                                )
                        )

                        # Add y-axis data for dev_max and dev_min lists
                        for i in range(num_dev_sublists):
                            print("i = {}, dev_max_str_list[i] = {}, dev_max[i] = {}, dev_min_str_list[i] = {}, \
                            dev_min[i] = {}".format(i, dev_max_str_list[i], dev_max[i], dev_min_str_list[i], dev_min[i]))
                            line.add_yaxis(dev_max_str_list[i], dev_max[i])
                            line.add_yaxis(dev_min_str_list[i], dev_min[i])

                        line.render(title_prefix + title_str + '.html')


# In[ ]:


import plotly.graph_objects as go
import os

def draw_html_for_results_plotly(dict_list, dev_str_mapping, \
                          DFS_min_list, DFS_max_list, RTC_source_list, times_list, PD_flash_flag_list, title_prefix):
       
    # 获取字典的键列表
    keys_list = list(dev_str_mapping.keys())
    
    dev_max_str_list = dev_str_mapping.get(keys_list[0], [])
    dev_min_str_list = dev_str_mapping.get(keys_list[1], [])
    
    for DFS_min in DFS_min_list:
        for DFS_max in DFS_max_list:
            for RTC_source in RTC_source_list:
                for times in times_list:
                    for PD_flash_flag in PD_flash_flag_list:
                        num_dev_sublists = len(dev_max_str_list)
                        dev_max = [[] for _ in range(num_dev_sublists)]
                        dev_min = [[] for _ in range(num_dev_sublists)]

                        for obj in dict_list:
                            if obj['dfs_min'] == DFS_min and obj['dfs_max'] == DFS_max and obj['PD_flash_flag'] == PD_flash_flag:
                                if obj['times'] == times:
                                    for i in range(num_dev_sublists):
                                        dev_max[i].append(obj[keys_list[0]][i])
                                        dev_min[i].append(obj[keys_list[1]][i])

                        title_str = "DFS_" + str(DFS_min) + "~" + str(DFS_max) + "_" + str(times) + "*1s_" + PD_flash_flag
                        fig = go.Figure()
                        # Add y-axis data for dev_max and dev_min lists
                        for i in range(num_dev_sublists):
                            fig.add_trace(go.Scatter(x=RTC_source_list, y=dev_max[i], mode='lines+markers', name=dev_max_str_list[i], text=dev_max[i], textposition='top center'))
                            fig.add_trace(go.Scatter(x=RTC_source_list, y=dev_min[i], mode='lines+markers', name=dev_min_str_list[i], text=dev_min[i], textposition='bottom center'))


                        fig.update_layout(title=title_str, xaxis_title="RTC source", yaxis_title="偏差(us)")
                        
                        html_file_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'results')) + '/' + title_prefix + title_str + '.html'
                        fig.write_html(html_file_path)


                       

