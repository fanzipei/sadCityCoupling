#!/usr/bin/env python
# encoding: utf-8

import numpy as np
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
ratio = 1.0


def get_loc_idx(lat, lon, lat_min, lon_min, lat_max, lon_max):
    num_dislat = int((lat_max - lat_min + 0.00001) / 0.008)
    dis_lat = int((lat - lat_min) / 0.008)
    dis_lon = int((lon - lon_min) / 0.010)

    return dis_lat + dis_lon * num_dislat


def get_transition_matrix(num_lat, num_lon, ratio):
    transition_matrix = []
    dis_matrix = np.zeros([num_loc_o, num_loc_o])
    for loc_1 in xrange(num_loc_o):
        for loc_2 in xrange(num_loc_o):
            lat_1 = loc_1 % num_lat
            lon_1 = loc_1 / num_lat
            lat_2 = loc_2 % num_lat
            lon_2 = loc_2 / num_lat
            if lat_1 == lat_2 and lon_1 == lon_2:
                dis_matrix[(loc_1, loc_2)] = 0.34
            else:
                dis_matrix[(loc_1, loc_2)] = ((lat_1 - lat_2) ** 2 + (lon_1 - lon_2) ** 2) ** 0.5

    transition_matrix.append((0.34 - 1) * np.log(dis_matrix) - dis_matrix)
    for i in xrange(1, 65):
        transition_matrix.append((i - 1) * np.log(dis_matrix) - dis_matrix)

    return transition_matrix


def get_distance_matrix(num_loc, num_lat):
    distance_matrix = np.zeros([num_loc, num_loc], np.int32)
    for i in xrange(num_loc):
        for j in xrange(num_loc):
            dis_lat_i = i % num_lat
            dis_lon_i = i / num_lat
            dis_lat_j = j % num_lat
            dis_lon_j = j / num_lat
            distance_matrix[(i, j)] = (int)(((dis_lat_i - dis_lat_j) ** 2 + (dis_lon_i - dis_lon_j) ** 2) ** 0.5)

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
            if lat < lat_min or lat >= lat_max or lon < lon_min or lon >= lon_max:
                continue
            lidx = get_loc_idx(lat, lon, lat_min, lon_min, lat_max, lon_max)

            tidx = int(tstamp - init_time) / 3600
            if tidx < 0 or tidx >= 24 or lidx < 0 or lidx >= num_loc:
                continue

            if u not in traj_set:
                if len(traj_set) < 10000:
                    traj_set[u] = [[lidx, time_str, -1]]
            else:
                traj_set[u].append([lidx, time_str, -1])

    return traj_set


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
            for lidx_t, time_str, lidx_o in traj_set[u]:
                if lidx_o < 0:
                    continue
                lat, lon = get_random_coordinates(lidx_o)
                f.write('{},{},{},{}\n'.format(u, lat, lon, time_str))


def read_P(filename):
    return np.genfromtxt(filename, delimiter = ',').T


def hmm_singleuser_inference(single_user_traj, P, transition_matrix, distance_matrix):
    traj_len = len(single_user_traj)
    delta = np.zeros([traj_len, num_loc_o])
    phi = []

    if traj_len <= 1:
        t_random = 0
    else:
        t_random = np.random.randint(1, traj_len)

    for t in xrange(1, traj_len):
        lidx_t = single_user_traj[t][0]
        lidx_t_pre = single_user_traj[t-1][0]
        trans_idx = distance_matrix[(lidx_t, lidx_t_pre)]
        tmp_matrix = delta[t-1] + transition_matrix[trans_idx]
        if t == t_random:
            P_rand = np.zeros(P.shape[1]) + np.log(1e-5)
            lidx_o = np.random.multinomial(1, (np.exp(P[lidx_t])/(np.sum(np.exp(P[lidx_t]))))).argmax()
            P_rand[lidx_o] = np.log(0.98)
            delta[t] = np.max(tmp_matrix, axis=1) + P_rand
        else:
            delta[t] = np.max(tmp_matrix, axis=1) + P[lidx_t]
        phi.append(np.argmax(tmp_matrix, axis=1))

    last_best = np.argmax(delta[-1])
    for tr in xrange(1, traj_len):
        single_user_traj[-tr][2] = last_best
        last_best = phi[-tr][last_best]
    single_user_traj[0][2] = last_best

    return single_user_traj


def hmm_inference(traj_set, P, transition_matrix, distance_matrix):
    for u in traj_set:
        traj_set[u] = hmm_singleuser_inference(traj_set[u], P, transition_matrix, distance_matrix)
        print 'User {} complete'.format(u)

    return traj_set


def main():
    transition_matrix = get_transition_matrix(num_lat_o, num_lon_o, ratio)
    distance_matrix = get_distance_matrix(num_loc_t, num_lat_t)
    print 'Generate Transition Matrix complete'

    P = np.log(read_P('./dp_rst/P_ITER42.csv'))
    print 'Read P complete, shape = {}'.format(P.shape)

    traj_set = read_traj('/home/fan/work/data/20120601_tokyo_sorted.csv', lat_min_t, lat_max_t, lon_min_t, lon_max_t, num_loc_t)
    print 'Read Tokyo Trajectories complete'

    traj_set = hmm_inference(traj_set, P, transition_matrix, distance_matrix)
    print 'HMM Inference complete'

    output_simulated(traj_set, './simulated_osaka.csv')
    print 'Output complete'


if __name__ == '__main__':
    main()
