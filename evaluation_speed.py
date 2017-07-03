#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import time
import csv


def read_traj(filename, init_time_str):
    traj = dict({})
    init_time =  time.mktime(time.strptime(init_time_str, '%Y-%m-%d %H:%M:%S'))

    with open(filename, 'r') as f:
        for uid_str, lat_str, lon_str, time_str in csv.reader(f):
            uid = int(uid_str)
            lat = float(lat_str)
            lon = float(lon_str)
            tstamp = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
            if uid in traj:
                traj[uid].append((tstamp - init_time, lat, lon))
            else:
                traj[uid] = [(tstamp - init_time, lat, lon)]

    for u in traj:
        traj[u] = sorted( traj[u] , key = lambda x: x[0] )

    return traj


def get_speed_comparison(traj_rs, traj_cp1, traj_cp2, traj_gt):
    t_sum = np.zeros([96, 4]) + 1.0
    dist_sum = np.zeros([96, 4])
    for u in traj_rs:
        pre_rec = None
        for cur_rec in traj_rs[u]:
            if pre_rec == None:
                pre_rec = cur_rec
                continue
            else:
                pre_t, pre_lat, pre_lon = pre_rec
                cur_t, cur_lat, cur_lon = cur_rec
                dt = cur_t - pre_t
                d_lat = (cur_lat - pre_lat) / 0.008
                d_lon = (cur_lon - pre_lon) / 0.010
                v = ((d_lat ** 2 + d_lon ** 2) ** 0.5)
                dis_t = int((0.5 * (cur_t + pre_t)) / 1800)
                t_sum[dis_t, 0] += dt
                dist_sum[dis_t, 0] += v
                pre_rec = cur_rec

    for u in traj_cp1:
        pre_rec = None
        for cur_rec in traj_cp1[u]:
            if pre_rec == None:
                pre_rec = cur_rec
                continue
            else:
                pre_t, pre_lat, pre_lon = pre_rec
                cur_t, cur_lat, cur_lon = cur_rec
                dt = cur_t - pre_t
                d_lat = (cur_lat - pre_lat) / 0.008
                d_lon = (cur_lon - pre_lon) / 0.010
                v = ((d_lat ** 2 + d_lon ** 2) ** 0.5)
                dis_t = int((0.5 * (cur_t + pre_t)) / 1800)
                t_sum[dis_t, 1] += dt
                dist_sum[dis_t, 1] += v
                pre_rec = cur_rec

    for u in traj_cp2:
        pre_rec = None
        for cur_rec in traj_cp2[u]:
            if pre_rec == None:
                pre_rec = cur_rec
                continue
            else:
                pre_t, pre_lat, pre_lon = pre_rec
                cur_t, cur_lat, cur_lon = cur_rec
                dt = cur_t - pre_t
                d_lat = (cur_lat - pre_lat) / 0.008
                d_lon = (cur_lon - pre_lon) / 0.010
                v = ((d_lat ** 2 + d_lon ** 2) ** 0.5)
                dis_t = int((0.5 * (cur_t + pre_t)) / 1800)
                t_sum[dis_t, 2] += dt
                dist_sum[dis_t, 2] += v
                pre_rec = cur_rec

    for u in traj_gt:
        pre_rec = None
        for cur_rec in traj_gt[u]:
            if pre_rec == None:
                pre_rec = cur_rec
                continue
            else:
                pre_t, pre_lat, pre_lon = pre_rec
                cur_t, cur_lat, cur_lon = cur_rec
                dt = cur_t - pre_t
                d_lat = (cur_lat - pre_lat) / 0.008
                d_lon = (cur_lon - pre_lon) / 0.010
                v = ((d_lat ** 2 + d_lon ** 2) ** 0.5)
                dis_t = int((0.5 * (cur_t + pre_t)) / 1800)
                t_sum[dis_t, 3] += dt
                dist_sum[dis_t, 3] += v
                pre_rec = cur_rec

    dist_sum /= t_sum
    return dist_sum


def main():
    traj_rs = read_traj('/media/fan/HDPC-UT/ZDC/TrainingForMapping/simulated_osaka_8.csv', '2011-12-30 23:50:00')
    traj_cp1 = read_traj('./simulated_osaka_newyear_simple.csv', '2011-12-30 23:50:00')
    traj_cp2 = read_traj('./simulated_trajectories/simulated_osaka_1_wo.csv', '2011-12-30 23:50:00')
    traj_gt = read_traj('./gt_osaka_newyear.csv', '2011-12-30 23:50:00')
    speed_comparison = get_speed_comparison(traj_rs, traj_cp1, traj_cp2, traj_gt)
    np.savetxt('speed_comp.csv', speed_comparison, delimiter=',')


if __name__ == '__main__':
    main()
