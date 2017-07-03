#!/usr/bin/env python
# encoding: utf-8

import time
import csv
import random

num_user = 200


# Tokyo
lat_min_t = 35.5
lat_max_t = 35.796
lon_min_t = 139.4
lon_max_t = 139.9
num_loc_t = 1850
# Osaka
lat_min_o = 34.45
lat_max_o = 34.85
lon_min_o = 135.3
lon_max_o = 135.7
num_loc_o = 2000


def get_loc_idx(lat, lon, lat_min, lon_min, lat_max, lon_max):
    num_dislat = int((lat_max - lat_min + 0.00001) / 0.008)
    dis_lat = int((lat - lat_min) / 0.008)
    dis_lon = int((lon - lon_min) / 0.010)

    return dis_lat + dis_lon * num_dislat


def load_traj(filename, i, lat_min, lon_min, lat_max, lon_max, num_loc):
    print 'Load file:' + filename
    traj_set = dict({})

    init_time = time.mktime(time.strptime('2012-05-31 23:50:00', '%Y-%m-%d %H:%M:%S')) + i * 24 * 3600

    with open(filename, 'r') as f:
        for u_str, time_str, lat_str, lon_str in csv.reader(f):
            u = int(u_str)
            tstamp = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
            lat = float(lat_str)
            lon = float(lon_str)
            if lat >= lat_max or lat < lat_min or lon >= lon_max or lon < lon_min:
                continue
            lidx = get_loc_idx(lat, lon, lat_min, lon_min, lat_max, lon_max)
            tidx = int(tstamp - init_time) / 600
            if tidx < 0 or tidx >= 144 or lidx < 0 or lidx >= num_loc:
                continue

            if u not in traj_set:
                traj_set[u] = []

            traj_set[u].append((lidx, tidx))

    return traj_set


def trim_traj(traj):
    return dict((k, v) for k, v in traj.items() if len(v) >= 20)


def subsample(traj, sample_size):
    key_subset = random.sample(traj, sample_size)
    return dict({k:traj[k] for k in key_subset})


def savetofile(filename, traj_200):
    print 'Saving ' + filename
    with open(filename, 'w') as f:
        uidx = 0
        for u in traj_200:
            for (lidx, tidx) in traj_200[u]:
                f.write('{},{},{},{}\n'.format(u, uidx, lidx, tidx))
            uidx += 1


def main():
    for i in xrange(30):
        traj_t = load_traj('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/201206{:02d}.csv'.format(i+1), i, lat_min_t, lon_min_t, lat_max_t, lon_max_t, num_loc_t)
        traj_o = load_traj('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/201206{:02d}.csv'.format(i+1), i, lat_min_o, lon_min_o, lat_max_o, lon_max_o, num_loc_o)
        traj_t = trim_traj(traj_t)
        traj_o = trim_traj(traj_o)
        print 'Len Tokyo:{}'.format(len(traj_t))
        print 'Len Osaka:{}'.format(len(traj_o))
        for j in xrange(50):
            traj_t_small = subsample(traj_t, num_user)
            traj_o_small = subsample(traj_o, num_user)
            savetofile('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/traj{}/201206{:02d}_{}.csv'.format(num_user, i+1, j), traj_t_small)
            savetofile('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/traj{}/201206{:02d}_{}.csv'.format(num_user, i+1, j), traj_o_small)

    for i in xrange(31):
        traj_t = load_traj('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/201207{:02d}.csv'.format(i+1), i, lat_min_t, lon_min_t, lat_max_t, lon_max_t, num_loc_t)
        traj_o = load_traj('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/201207{:02d}.csv'.format(i+1), i, lat_min_o, lon_min_o, lat_max_o, lon_max_o, num_loc_o)
        traj_t = trim_traj(traj_t)
        traj_o = trim_traj(traj_o)
        print 'Len Tokyo:{}'.format(len(traj_t))
        print 'Len Osaka:{}'.format(len(traj_o))
        for j in xrange(50):
            traj_t_small = subsample(traj_t, num_user)
            traj_o_small = subsample(traj_o, num_user)
            savetofile('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/traj{}/201207{:02d}_{}.csv'.format(num_user, i+1, j), traj_t_small)
            savetofile('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/traj{}/201207{:02d}_{}.csv'.format(num_user, i+1, j), traj_o_small)


if __name__ == '__main__':
    main()
