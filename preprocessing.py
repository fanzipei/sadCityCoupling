#!/usr/bin/env python
# encoding: utf-8

import csv
import time


for m in xrange(6, 8):
    for d in xrange(1, 32):
        if m == 6 and d == 31:
            continue
        user_trajs = dict({})
        filename = '/media/fan/HDPC-UT/ZDC/TrainingForMapping/fukuoka/2012{:02d}{:02d}.csv'.format(m, d)
        print filename
        with open(filename, 'r') as f:
            for uid_str, lat_str, lon_str, time_str in csv.reader(f):
                u = int(uid_str)
                if u not in user_trajs:
                    user_trajs[u] = []
                user_trajs[u].append((float(lat_str), float(lon_str), time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S')), time_str))
        for u in user_trajs:
            user_trajs[u] = sorted(user_trajs[u], key=lambda x:x[2])

        filename = '/media/fan/HDPC-UT/ZDC/TrainingForMapping/fukuoka/sorted/2012{:02d}{:02d}.csv'.format(m, d)
        with open(filename, 'w') as f:
            for u in user_trajs:
                for lat, lon, tstamp, time_str in user_trajs[u]:
                    f.write('{},{},{},{}\n'.format(u, lat, lon, time_str))

for m in xrange(6, 8):
    for d in xrange(1, 32):
        if m == 6 and d == 31:
            continue
        user_trajs = dict({})
        filename = '/media/fan/HDPC-UT/ZDC/TrainingForMapping/nagano/2012{:02d}{:02d}.csv'.format(m, d)
        print filename
        with open(filename, 'r') as f:
            for uid_str, lat_str, lon_str, time_str in csv.reader(f):
                u = int(uid_str)
                if u not in user_trajs:
                    user_trajs[u] = []
                user_trajs[u].append((float(lat_str), float(lon_str), time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S')), time_str))
        for u in user_trajs:
            user_trajs[u] = sorted(user_trajs[u], key=lambda x:x[2])

        filename = '/media/fan/HDPC-UT/ZDC/TrainingForMapping/nagano/sorted/2012{:02d}{:02d}.csv'.format(m, d)
        with open(filename, 'w') as f:
            for u in user_trajs:
                for lat, lon, tstamp, time_str in user_trajs[u]:
                    f.write('{},{},{},{}\n'.format(u, lat, lon, time_str))
