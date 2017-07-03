#!/usr/bin/env python
# encoding: utf-8

import csv
import time
import numpy as np


# Tokyo
# lat_min = 35.5
# lat_max = 35.8
# lon_min = 139.4
# lon_max = 139.9
# Osaka
lat_min = 34.45
lat_max = 34.85
lon_min = 135.3
lon_max = 135.7
num_dislat = int( ( lat_max - lat_min + 0.00001 )/0.004 )
num_dislon = int( ( lon_max - lon_min + 0.00001 )/0.005 )


def get_lat_lon(loc_idx):
    lat_base = lat_min + ( loc_idx % num_dislat ) * 0.004 + 0.001
    lon_base = lon_min + ( loc_idx / num_dislat ) * 0.005 + 0.00125
    return lat_base + np.random.ranf() * 0.002, lon_base + np.random.ranf() * 0.0025


def read_file(filename):
    graph_dict = dict({})
    with open(filename,'r') as f:
        for loc_ori_str,loc_des_str,cnt_str in csv.reader(f):
            loc_ori = int(loc_ori_str)
            loc_des = int(loc_des_str)
            cnt = int(cnt_str)
            graph_dict[(loc_ori,loc_des)] = cnt

    return graph_dict


def output_visualization(filename, graph_dict,time_idx):
    uid = 0
    ori_time = time.mktime(time.strptime('2012-06-01 12:00:00','%Y-%m-%d %H:%M:%S')) + time_idx * 1800 - 1800
    des_time = ori_time + 3600

    with open(filename, 'w') as f:
        for loc_ori, loc_des in graph_dict:
            cnt = graph_dict[(loc_ori,loc_des)]
            for i in xrange(cnt):
                lat_ori, lon_ori = get_lat_lon(loc_ori)
                lat_des, lon_des = get_lat_lon(loc_des)
                f.write('{},{},{},{}\n'.format(uid,lat_ori,lon_ori,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(ori_time))))
                f.write('{},{},{},{}\n'.format(uid,lat_des,lon_des,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(des_time))))
                uid += 1


def main():
    for i in xrange(2880):
        graph_dict = read_file('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/mobilitygraph/graph_H{}_30.csv'.format(i))
        output_visualization('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/visualization_graph/visgraph_H{}_30.csv'.format(i), graph_dict,i)


if __name__ == '__main__':
    main()
