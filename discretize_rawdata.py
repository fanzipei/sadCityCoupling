#!/usr/bin/env python
# encoding: utf-8

import csv
import time

# Tokyo
lat_min_t = 35.5
lat_max_t = 35.796
lon_min_t = 139.4
lon_max_t = 139.9
# Osaka
lat_min_o = 34.45
lat_max_o = 34.85
lon_min_o = 135.3
lon_max_o = 135.7
# Fukuoka
lat_min_f = 33.48
lat_max_f = 33.76
lon_min_f = 130.25
lon_max_f = 130.7
# Nagoya
lat_min_n = 35.00
lat_max_n = 35.32
lon_min_n = 136.7
lon_max_n = 137.1


def get_loc_idx(lat, lon, lat_min, lon_min, lat_max, lon_max, num_dislat):
    dis_lat = int((lat - lat_min) / 0.008)
    dis_lon = int((lon - lon_min) / 0.010)

    return dis_lat + dis_lon * num_dislat


lat_min = lat_min_t
lon_min = lon_min_t
lat_max = lat_max_t
lon_max = lon_max_t
num_dislat = int((lat_max - lat_min + 1e-6) / 0.008)
num_dislon = int((lon_max - lon_min + 1e-6) / 0.010)

for m in xrange(6, 8):
    for d in xrange(1 , 32):
        if m == 6 and d == 31:
            continue
        user_index= dict({})
        filename = '/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/sorted/2012{:02d}{:02d}.csv'.format(m, d)
        init_time = time.mktime(time.strptime('2012-{:02d}-{:02d} 00:00:00'.format(m, d), '%Y-%m-%d %H:%M:%S')) - 600
        print filename
        filename_out = '/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/discretized/2012{:02d}{:02d}.csv'.format(m, d)
        with open(filename_out, 'w') as fout:
            with open(filename, 'r') as f:
                for uid_str, lat_str, lon_str, time_str in csv.reader(f):
                    tstamp = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
                    if tstamp < init_time or tstamp >= init_time + 24 * 3600:
                        continue
                    tidx = int((tstamp - init_time) / 1200)
                    u = int(uid_str)
                    if u not in user_index:
                        user_index[u] = len(user_index)
                    uidx = user_index[u]
                    lidx = get_loc_idx(float(lat_str), float(lon_str), lat_min, lon_min, lat_max, lon_max, num_dislat)
                    fout.write('{},{},{}\n'.format(uidx, lidx, tidx))

