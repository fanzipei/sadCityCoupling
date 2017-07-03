#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import math
import time
import csv


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

num_lat_t = 37
num_lon_t = 40
num_lat_o = 50
num_lon_o = 40

num_time = 72


def get_loc_idx(lat, lon, lat_min, lon_min, lat_max, lon_max):
    num_dislat = int((lat_max - lat_min + 0.00001) / 0.008)
    dis_lat = int((lat - lat_min) / 0.008)
    dis_lon = int((lon - lon_min) / 0.010)

    return dis_lat + dis_lon * num_dislat


def get_distance_matrix(num_loc, num_lat):
    distance_matrix = np.zeros([num_loc, num_loc], np.float)
    for i in xrange(num_loc):
        for j in xrange(num_loc):
            dis_lat_i = i % num_lat
            dis_lon_i = i / num_lat
            dis_lat_j = j % num_lat
            dis_lon_j = j / num_lat
            distance_matrix[(i, j)] = (((dis_lat_i - dis_lat_j) ** 2 + (dis_lon_i - dis_lon_j) ** 2) ** 0.5) + 0.4

    return distance_matrix


def read_traj(filename, lat_min, lat_max, lon_min, lon_max, num_loc):
    traj_set = dict({})
    init_time = time.mktime(time.strptime('2012-05-31 23:50:00', '%Y-%m-%d %H:%M:%S'))

    with open(filename, 'r') as f:
        for u_str, time_str, lat_str, lon_str in csv.reader(f):
            u = int(u_str)
            tstamp = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
            lat = float(lat_str)
            lon = float(lon_str)
            lidx = get_loc_idx(lat, lon, lat_min, lon_min, lat_max, lon_max)
            tidx = int(tstamp - init_time) / ((3600 * 24) / num_time)

            if lat < lat_min or lat >= lat_max or lon < lon_min or lon >= lon_max:
                continue
            if tidx < 0 or tidx >= num_time:
                continue

            if u not in traj_set:
                traj_set[u] = [[lidx, tidx, time_str]]
            else:
                traj_set[u].append([lidx, tidx, time_str])

    return traj_set


def read_P(filename):
    return np.genfromtxt(filename, delimiter = ',').T


def get_time_loc_estimation(traj_set, P):
    time_loc_expectation = np.zeros([num_time, num_loc_o], np.float)
    for u in traj_set:
        for lidx, tidx, time_str in traj_set[u]:
            time_loc_expectation[tidx] += P[lidx]

    return time_loc_expectation


def hmm_singleuser_inference(single_user_traj, logP, P, log_distance_matrix_o_array, dtime_loc):
    traj_len = len(single_user_traj)
    delta = np.zeros([traj_len, num_loc_o])
    phi = []

    if traj_len <= 1:
        lidx_t = single_user_traj[0][1]
        single_user_traj[0][0] = np.random.multinomial(1, P[lidx_t]).argmax()
        return single_user_traj

    for t in xrange(1, traj_len):
        lidx_t = single_user_traj[t][1]
        tidx_t = single_user_traj[t][2]
        dist_t = single_user_traj[t][4]
        tmp_matrix = delta[t-1] + log_distance_matrix_o_array[dist_t]
        delta[t] = np.max(tmp_matrix, axis=1) + logP[lidx_t] - 0.01 * (2 * dtime_loc[tidx_t] + 1)
        phi.append(np.argmax(tmp_matrix, axis=1))

    last_best = np.argmax(delta[-1])
    for tr in xrange(1, traj_len):
        single_user_traj[-tr][0] = last_best
        last_best = phi[-tr][last_best]
    single_user_traj[0][0] = last_best

    return single_user_traj


def mcmc_inference(traj_t, P, time_loc_expectation, distance_matrix_t, log_distance_matrix_o_array, max_iter):
    traj_o = dict({})
    logP = np.log(P + 1e-30)
    time_loc_cnt = np.zeros([num_time, num_loc_o], np.float)

    for u in traj_t:
        traj_o[u] = []

        lidx_t_pre = traj_t[u][0][0]
        for lidx_t, tidx, time_str in traj_t[u]:
            lidx_o = np.random.multinomial(1, P[lidx_t]).argmax()
            time_loc_cnt[tidx, lidx_o] += 1.0
            traj_o[u].append([lidx_o, lidx_t, tidx, time_str, distance_matrix_t[lidx_t_pre, lidx_t]])
            lidx_t_pre = lidx_t

    dtime_loc = time_loc_cnt - time_loc_expectation
    print 'Random Initialization complete'

    for i in xrange(max_iter):
        print 'Iteration {}'.format(i)
        traj_user_list = list(traj_o)
        np.random.shuffle(traj_user_list)
        for u in traj_user_list:
            for lidx_o, lidx_t, tidx, time_str, dist_t in traj_o[u]:
                dtime_loc[tidx, lidx_o] -= 1
            hmm_singleuser_inference(traj_o[u], logP, P, log_distance_matrix_o_array, dtime_loc)
            for lidx_o, lidx_t, tidx, time_str, dist_t in traj_o[u]:
                dtime_loc[tidx, lidx_o] += 1

        yield i, traj_o


def get_random_coordinates(lidx_o):
    num_dislat = int((lat_max_o - lat_min_o + 0.00001) / 0.008)
    dis_lat = lidx_o % num_dislat
    dis_lon = lidx_o / num_dislat
    lat = lat_min_o + 0.008 * dis_lat + 0.002 + 0.004 * np.random.ranf()
    lon = lon_min_o + 0.010 * dis_lon + 0.0025 + 0.005 * np.random.ranf()
    return lat, lon


def output_simulated(traj_set, filename):
    with open(filename, 'w')  as f:
        for u in traj_set:
            for lidx_o, lidx_t, tidx, time_str, dist_t in traj_set[u]:
                if lidx_o < 0:
                    continue
                lat, lon = get_random_coordinates(lidx_o)
                f.write('{},{},{},{}\n'.format(u, lat, lon, time_str))


def main():
    distance_matrix_o = get_distance_matrix(num_loc_o, num_lat_o)
    distance_matrix_t = get_distance_matrix(num_loc_t, num_lat_t)
    distance_matrix_t = np.round(distance_matrix_t).astype(int)
    log_distance_matrix_o_array = [ -math.lgamma(i + 0.4) + (i-0.6) * np.log(distance_matrix_o) - distance_matrix_o for i in xrange(np.max(distance_matrix_t)+1)]
    print 'Farest distance = {}'.format(np.max(distance_matrix_t))
    print 'Generate Transition Matrix complete'

    traj_t = read_traj('/home/fan/work/data/20120601_tokyo_sorted.csv', lat_min_t, lat_max_t, lon_min_t, lon_max_t, num_loc_t)
    print 'Read Tokyo Trajectories complete'

    P = read_P('./dp_rst/P_ITER199.csv')
    print 'Read P complete, shape = {}'.format(P.shape)

    time_loc_expectation = get_time_loc_estimation(traj_t, P)
    print 'Get time loc expectation matrix'

    for i, traj_o in mcmc_inference(traj_t, P, time_loc_expectation, distance_matrix_t, log_distance_matrix_o_array, 1000000):
        output_simulated(traj_o, './simulated_trajectories/simulated_osaka_{}.csv'.format(i+1))
        print 'Output complete'


if __name__ == '__main__':
    main()
