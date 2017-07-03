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

def itemgetter(item):
    return item[2]


def estimated_location(traj, t):
    pre_rec = traj[0]
    cur_rec = traj[0]
    for rec in traj:
        cur_lat,cur_lon,cur_t = rec
        pre_lat,pre_lon,pre_t = pre_rec
        if cur_t < t:
            pre_rec = cur_rec
            cur_rec = rec
        else:
            dt = cur_t - pre_t
            dlat = cur_lat - pre_lat
            dlon = cur_lon - pre_lon
            lat = pre_lat + ( t - pre_t ) * dlat / ( dt + 0.0000001 )
            lon = pre_lon + ( t - pre_t ) * dlon / ( dt + 0.0000001 )

    lat,lon,last_t = cur_rec
    return int((lat - lat_min)/0.008),int((lon - lon_min)/0.010)


def example_generator(traj_dis_rs, traj_dis_gt, t_beg, t_end):
    example_set = []
    init_loc_rs = dict({})
    init_loc_gt = dict({})

    for u in traj_rs:
        lat,lon,tstamp = traj_rs[u][0]
        init_loc_rs[u] = (int((lat - lat_min)/0.008),int((lon - lon_min)/0.010))
    for u in traj_gt:
        lat,lon,tstamp = traj_gt[u][0]
        init_loc_gt[u] = (int((lat - lat_min)/0.008),int((lon - lon_min)/0.010))

    for t in xrange(start_time,end_time,time_step):
        loc_rs = getLocationByTime(traj_rs,t)
        loc_gt = getLocationByTime(traj_gt,t)
        example_bytime = getExampleByTime(init_loc_rs,init_loc_gt,loc_rs,loc_gt)
        example_set.append(example_bytime)

    return example_set


def output_examples(examples,t,outpath):
    time_gap = 0
    for example_bytime in examples:
        time_gap += 10
        filename = outpath + 'T{}P{}m.csv'.format(t,time_gap)
        with open(filename,'w') as f:
            for init_loc in example_bytime:
                init_dis_lat,init_dis_lon = init_loc
                print len(example_bytime[init_loc])
                for cur_loc,count in example_bytime[init_loc].iteritems():
                    dis_lat,dis_lon = cur_loc
                    count_rs = count[0]
                    count_gt = count[1]
                    f.write('{},{},{},{},{},{}\n'.format(init_dis_lat,init_dis_lon,dis_lat,dis_lon,count_rs,count_gt))


def loadfile(filename):
    traj_set = dict({})
    with open(filename,'r') as f:
        for u_str,lat_str,lon_str,time_str in csv.reader(f):
            u = int(u_str)
            lat = float( lat_str )
            lon = float( lon_str )
            tstamp = time.mktime(time.strptime(time_str,'%Y-%m-%d %H:%M:%S'))
            if u in traj_set:
                traj_set[u].append((lat,lon,tstamp))
            else:
                traj_set[u] = [(lat,lon,tstamp)]

    for u in traj_set:
        sorted( traj_set[u] , key = itemgetter )

    return traj_set


def get_discrete_time_traj(traj, init_time, max_time):
    traj_dis = dict({})
    for u in traj:
        traj_dis[u] = []
        for t in xrange(max_time):
            dis_lat, dis_lon = estimated_location(traj[u], init_time + 600 * t)
            traj_dis[u].append((dis_lat, dis_lon))

    return traj_dis


def get_density_variation(traj_dis_rs, traj_dis_gt, path, max_time):
    density_map_rs = np.zeros([n_lat, n_lon, max_time])
    density_map_gt = np.zeros([n_lat, n_lon, max_time])
    for u in traj_dis_rs:
        for t in xrange(max_time):
            dis_lat, dis_lon = traj_dis_rs[u][t]
            density_map_rs[dis_lat, dis_lon, t] += 1

    for u in traj_dis_gt:
        for t in xrange(max_time):
            dis_lat, dis_lon = traj_dis_gt[u][t]
            density_map_gt[dis_lat, dis_lon, t] += 1

    for dis_lat in xrange(n_lat):
        for dis_lon in xrange(n_lon):
            filename = 'LAT{}LON{}.csv'.format(dis_lat, dis_lon)
            with open(path + filename, 'w') as f:
                for t in xrange(max_time):
                    f.write('{},{}\n'.format(density_map_rs[dis_lat, dis_lon, t], density_map_gt[dis_lat, dis_lon, t]))


def main():
    init_time = time.mktime(time.strptime('2011-12-30 23:50:00','%Y-%m-%d %H:%M:%S'))
    traj_rs = loadfile('/media/fan/HDPC-UT/ZDC/TrainingForMapping/simulated_osaka_8.csv')
    traj_gt = loadfile('/home/fan/work/python/sadCityMapping/gt_osaka_newyear.csv')
    traj_dis_rs = get_discrete_time_traj(traj_rs, init_time, 6 * 24 * 2)
    traj_dis_gt = get_discrete_time_traj(traj_gt, init_time, 6 * 24 * 2)
    get_density_variation(traj_dis_rs, traj_dis_gt, './density_variation/', 6 * 24 * 2)
    #  for t in xrange(6, 6 * 24 * 2):
        #  examples = example_generator(traj_dis_rs, traj_dis_gt, t - 6, t)
        #  output_examples(examples, t, './evaluation_newyear/')

if __name__ == '__main__':
    main()
