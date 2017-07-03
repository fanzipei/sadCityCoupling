#!/usr/bin/env python
# encoding: utf-8

import csv
import time
import numpy as np

# Osaka
lat_min = 34.45
lat_max = 34.85
lon_min = 135.3
lon_max = 135.7

n_lat = 50
n_lon = 40

max_time = 288
time_interval = 600


def itemgetter(item):
    return item[0]


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
            dis_t = max(min((tstamp - init_time) / time_interval, max_time), 0)
            if uid in traj:
                traj[uid].append((dis_t, dis_lat, dis_lon))
            else:
                traj[uid] = [(dis_t, dis_lat, dis_lon)]

    return traj


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
        traj[u] = sorted( traj[u] , key = itemgetter )

    return traj


def generate_density_map(traj):
    density_variation = np.zeros([n_lat, n_lon, max_time])
    n_u = len(traj) + 0.01
    for u in traj:
        for dis_t, dis_lat, dis_lon in traj[u]:
            density_variation[dis_lat, dis_lon, dis_t] += 1.0 / n_u

    return density_variation


def output_density_variation(density_variation_rs, density_variation_cp, density_variation_gt, path):
    for dis_lat in xrange(n_lat):
        for dis_lon in xrange(n_lon):
            filename = 'LAT{}LON{}.csv'.format(dis_lat, dis_lon)
            with open(path + filename, 'w') as f:
                for t in xrange(max_time):
                    f.write('{},{},{}\n'.format(density_variation_rs[dis_lat, dis_lon, t], density_variation_cp[dis_lat, dis_lon, t], density_variation_gt[dis_lat, dis_lon, t]))


def example_generator(traj_rs, traj_cp1, traj_cp2, traj_gt, t_beg, t_end):
    examples = dict({})
    for u in traj_rs:
        loc_beg = estimated_location(traj_rs[u], t_beg)
        loc_end = estimated_location(traj_rs[u], t_end)
        if loc_beg in examples:
            if loc_end in examples[loc_beg]:
                examples[loc_beg][loc_end][0] += 1
            else:
                examples[loc_beg][loc_end] = [1, 0, 0, 0]
        else:
            examples[loc_beg] = dict({})
            examples[loc_beg][loc_end] = [1, 0, 0, 0]

    for u in traj_cp1:
        loc_beg = estimated_location(traj_cp1[u], t_beg)
        loc_end = estimated_location(traj_cp1[u], t_end)
        if loc_beg in examples:
            if loc_end in examples[loc_beg]:
                examples[loc_beg][loc_end][1] += 1
            else:
                examples[loc_beg][loc_end] = [0, 1, 0, 0]
        else:
            examples[loc_beg] = dict({})
            examples[loc_beg][loc_end] = [0, 1, 0, 0]

    for u in traj_cp2:
        loc_beg = estimated_location(traj_cp2[u], t_beg)
        loc_end = estimated_location(traj_cp2[u], t_end)
        if loc_beg in examples:
            if loc_end in examples[loc_beg]:
                examples[loc_beg][loc_end][2] += 1
            else:
                examples[loc_beg][loc_end] = [0, 0, 1, 0]
        else:
            examples[loc_beg] = dict({})
            examples[loc_beg][loc_end] = [0, 0, 1, 0]

    for u in traj_gt:
        loc_beg = estimated_location(traj_gt[u], t_beg)
        loc_end = estimated_location(traj_gt[u], t_end)
        if loc_beg in examples:
            if loc_end in examples[loc_beg]:
                examples[loc_beg][loc_end][3] += 1
            else:
                examples[loc_beg][loc_end] = [0, 0, 0, 1]
        else:
            examples[loc_beg] = dict({})
            examples[loc_beg][loc_end] = [0, 0, 0, 1]

    return examples


def output_examples(examples, t, path, k):
    filename = path + 'T{}P{}0m.csv'.format(t, k)
    with open(filename, 'w') as f:
        for beg_loc in examples:
            beg_dis_lat, beg_dis_lon = beg_loc
            for cur_loc in examples[beg_loc]:
                count_rs, count_cp1, count_cp2, count_gt = examples[beg_loc][cur_loc]
                dis_lat, dis_lon = cur_loc
                f.write('{},{},{},{},{},{},{},{}\n'.format(beg_dis_lat, beg_dis_lon, dis_lat, dis_lon, count_rs, count_gt, count_cp1, count_cp2))


def estimated_location(traj, t):
    pre_rec = traj[0]
    cur_rec = traj[0]
    for rec in traj:
        cur_t, cur_lat, cur_lon = rec
        pre_t, pre_lat, pre_lon = pre_rec
        if cur_t < t:
            pre_rec = cur_rec
            cur_rec = rec
        else:
            dt = cur_t - pre_t
            dlat = cur_lat - pre_lat
            dlon = cur_lon - pre_lon
            lat = pre_lat + ( t - pre_t ) * dlat / ( dt + 0.0000001 )
            lon = pre_lon + ( t - pre_t ) * dlon / ( dt + 0.0000001 )

    last_t, lat, lon = cur_rec
    return (int((lat - lat_min)/0.008), int((lon - lon_min)/0.010))


def main():
    traj_rs = read_traj('/media/fan/HDPC-UT/ZDC/TrainingForMapping/simulated_osaka_8.csv', '2011-12-30 23:50:00')
    traj_cp1 = read_traj('./simulated_osaka_newyear_simple.csv', '2011-12-30 23:50:00')
    traj_cp2 = read_traj('./simulated_trajectories/simulated_osaka_1_wo.csv', '2011-12-30 23:50:00')
    traj_gt = read_traj('./gt_osaka_newyear.csv', '2011-12-30 23:50:00')
    #  density_variation_rs = generate_density_map(traj_rs)
    #  density_variation_cp = generate_density_map(traj_cp)
    #  density_variation_gt = generate_density_map(traj_gt)
    #  output_density_variation(density_variation_rs, density_variation_cp, density_variation_gt, './density_variation/')
    for t in xrange(0, max_time - 6):
        print 't = {}'.format(t)
        examples_20 = example_generator(traj_rs, traj_cp1, traj_cp2, traj_gt, t * time_interval, (t + 2) * time_interval)
        examples_40 = example_generator(traj_rs, traj_cp1, traj_cp2, traj_gt, t * time_interval, (t + 4) * time_interval)
        examples_60 = example_generator(traj_rs, traj_cp1, traj_cp2, traj_gt, t * time_interval, (t + 6) * time_interval)
        output_examples(examples_20, t, './evaluation_examples/', 2)
        output_examples(examples_40, t, './evaluation_examples/', 4)
        output_examples(examples_60, t, './evaluation_examples/', 6)


if __name__ == '__main__':
    main()
