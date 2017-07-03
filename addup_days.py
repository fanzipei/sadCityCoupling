#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import csv

graph_dict = dict({})

def read_file(filename,t):
    with open(filename,'r') as f:
        for loc_ori_str,loc_des_str,cnt_str in csv.reader(f):
            loc_ori = int(loc_ori_str)
            loc_des = int(loc_des_str)
            cnt = int(cnt_str)
            if loc_ori == loc_des:
                print 'Error'
            else:
                if (loc_ori,loc_des) not in graph_dict:
                    graph_dict[(loc_ori,loc_des)] = np.zeros(48,np.int32)
                    graph_dict[(loc_ori,loc_des)][t%48] = cnt
                else:
                    graph_dict[(loc_ori,loc_des)][t%48] += cnt

def output_edge_file(filename,t):
    with open(filename,'w') as f:
        for (loc_ori,loc_des) in graph_dict:
            if graph_dict[(loc_ori,loc_des)][t] > 0:
                f.write('{},{},{}\n'.format(loc_ori,loc_des,graph_dict[(loc_ori,loc_des)][t]))

def main():
    read_file('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/mobilitygraph_large/graph_H{}_30.csv'.format(d),d)
    output_edge_file('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/aggregated_mobilitygraph/agraph_30.csv')
