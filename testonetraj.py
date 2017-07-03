#!/usr/bin/env python
# encoding: utf-8

import csv
import time
import numpy as np

# Tokyo
lat_min_t = 35.5
lat_max_t = 35.8
lon_min_t = 139.4
lon_max_t = 139.9
num_loc_t = 7500
num_dislat_t = int( ( lat_max_t - lat_min_t + 0.00001 )/0.008 )
# Osaka
lat_min_o = 34.45
lat_max_o = 34.85
lon_min_o = 135.3
lon_max_o = 135.7
num_loc_o = 8000
num_dislat_o = int( ( lat_max_o - lat_min_o + 0.00001 )/0.008 )

def get_dis_loc(lat,lon):
    dis_lat = int( ( lat - lat_min_t )/0.008 )
    dis_lon = int( ( lon - lon_min_t )/0.010 )
    return dis_lat,dis_lon

def read_traj(filename):
    traj = []
    with open(filename,'r') as f:
        for uid_str,time_str,lat_str,lon_str,tmp1_str,tmp2_str,tmp3_str,tmp4_str in csv.reader(f):
            tstamp = time.mktime(time.strptime(time_str,'%Y-%m-%d %H:%M:%S'))
            lat = float(lat_str)
            lon = float(lon_str)
            loc_idx = get_dis_loc(lat,lon)
            traj.append((loc_idx,tstamp))

    return traj


def read_transition_matrix(filename):
    with open(filename,'r') as f:
        w_reader = csv.reader(f)
        w_array = list(w_reader)

    return np.array(w_array).astype('float')


def estimated_location(traj,t):
    pre_rec = traj[0]
    for rec in traj:
        cur_lat,cur_lon,cur_t = rec
        pre_lat,pre_lon,pre_t = pre_rec
        if cur_t < t:
            pre_rec = rec
        else:
            dt = cur_t - pre_t
            dlat = cur_lat - pre_lat
            dlon = cur_lon - pre_lon
            lat = pre_lat + ( t - pre_t ) * dlat / ( dt + 0.0000001 )
            lon = pre_lon + ( t - pre_t ) * dlon / ( dt + 0.0000001 )
            return lat,lon
    lat,lon,last_t = pre_rec
    return lat,lon


def transfer_traj(traj, outfile):
    with open(outfile,'w') as f:
        init_lat,init_lon,init_t = traj[0]
        for t in xrange(1000):
            cur_t = init_t + 600 * t
            lat,lon = estimated_location(traj,cur_t)
            dis_lat,dis_lon = get_dis_loc(lat,lon)
            filename = '/home/fan/work/python/sadCityMapping/visualization/LAT{}LON{}.txt'.format(dis_lat,dis_lon)
            f.write(filename+'\n')


def main():
    traj = read_traj('./00000233.csv')
    print 'Read Traj Complete'
    P = read_transition_matrix('./W_A002B025ITA0001ITR100.csv')
    # print 'Read Transition Matrix Complete'
    # print W.shape
    transfer_traj(traj, './transfer_traj_233.txt')


if __name__ == '__main__':
    main()
