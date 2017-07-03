#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import time
import csv

# Osaka
lat_min = 34.45
lat_max = 34.85
lon_min = 135.3
lon_max = 135.7

n_lat = 50
n_lon = 40

max_time = 96
time_interval = 1800


def read_dis_traj(filename, init_time_str):
    traj = dict({})
    init_time =  time.mktime(time.strptime(init_time_str, '%Y-%m-%d %H:%M:%S'))

    with open(filename, 'r') as f:
        for uid_str, lat_str, lon_str, time_str in csv.reader(f):
            uid = int(uid_str)
            lat = float(lat_str)
            lon = float(lon_str)
            dis_lat = min((lat - lat_min) / 0.008, n_lat)
            dis_lon = min((lon - lon_min) / 0.010, n_lon)
            tstamp = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
            dis_t = max(min((tstamp - init_time) / time_interval, max_time - 1), 0)
            if uid in traj:
                traj[uid].append((dis_t, dis_lat, dis_lon))
            else:
                traj[uid] = [(dis_t, dis_lat, dis_lon)]

    return traj


def generate_density_map(traj):
    density_variation = np.zeros([n_lat, n_lon, max_time])
    n_u = len(traj) + 0.01
    for u in traj:
        for dis_t, dis_lat, dis_lon in traj[u]:
            density_variation[dis_lat, dis_lon, dis_t] += 1.0 / n_u

    return density_variation


def output_density_variation(density_variation_rs, path):
    for dis_lat in xrange(n_lat):
        for dis_lon in xrange(n_lon):
            filename = 'LAT{}LON{}.csv'.format(dis_lat, dis_lon)
            with open(path + filename, 'w') as f:
                for t in xrange(max_time):
                    f.write('{}\n'.format(density_variation_rs[dis_lat, dis_lon, t]))


def main():
    traj_rs = read_dis_traj('./simulated_trajectories/simulated_osaka_1_wo.csv', '2011-12-30 23:50:00')
    density_variation_rs = generate_density_map(traj_rs)
    output_density_variation(density_variation_rs, './density_variation_noglobal/')


if __name__ == '__main__':
    main()
