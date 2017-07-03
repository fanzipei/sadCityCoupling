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


def main():
    with open('/media/fan/HDPC-UT/ZDC/TrainingNewyear/20120101.csv', 'r') as f_in:
        with open('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/20120101.csv', 'w') as f_out_t:
            with open('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/20120101.csv', 'w') as f_out_o:
                for uid_str, time_str, lat_str, lon_str, tmp1_str, tmp2_str in csv.reader(f_in):
                    uid = int(uid_str)
                    cur_time = time.mktime(time.strptime(time_str,'%Y-%m-%d %H:%M:%S'))
                    lat = float(lat_str)
                    lon = float(lon_str)
                    if lat > lat_min_t and lat < lat_max_t and lon > lon_min_t and lon < lon_max_t:
                        f_out_t.write('{},{},{},{}\n'.format(uid, lat, lon, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(cur_time))))
                    elif lat > lat_min_o and lat < lat_max_o and lon > lon_min_o and lon < lon_max_o:
                        f_out_o.write('{},{},{},{}\n'.format(uid, lat, lon, time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(cur_time))))


if __name__ == '__main__':
    main()
