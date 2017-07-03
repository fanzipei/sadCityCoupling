#!/usr/bin/env python
# encoding: utf-8

import csv
import time
import numpy as np


# Osaka
lat_min_o = 34.45
lat_max_o = 34.85
lon_min_o = 135.3
lon_max_o = 135.7
num_loc_o = 2000


def read_traj(filename, outfile, lat_min, lat_max, lon_min, lon_max):
    init_time = time.mktime(time.strptime('2011-12-30 23:50:00', '%Y-%m-%d %H:%M:%S'))

    with open(filename, 'r') as f:
        with open(outfile, 'w') as fout:
            for u_str, lat_str, lon_str, time_str in csv.reader(f):
                tstamp = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
                lat = float(lat_str)
                lon = float(lon_str)
                dis_lat = int((lat - lat_min) / 0.008)
                dis_lon = int((lon - lon_min) / 0.010)
                lat_resample = lat_min + dis_lat * 0.008 + 0.002 + 0.004 * np.random.ranf()
                lon_resample = lon_min + dis_lon * 0.010 + 0.0025 + 0.005 * np.random.ranf()

                tidx = int(tstamp - init_time) / 3600
                if tidx < 0 or tidx >= 48:
                    continue
                fout.write('{},{},{},{}\n'.format(u_str, lat_resample, lon_resample, time_str))


def main():
    read_traj('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/2011newyear.csv', './gt_osaka_newyear.csv', lat_min_o, lat_max_o, lon_min_o, lon_max_o)


if __name__ == '__main__':
    main()
