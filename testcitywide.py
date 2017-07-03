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
num_dislat_t = 37
num_loc_t = 1850
# Osaka
lat_min_o = 34.45
lat_max_o = 34.85
lon_min_o = 135.3
lon_max_o = 135.7
num_dislat_o = 50
num_loc_o = 2000

MAX_GIBBS_ITERATION = 10


def get_loc_idx(lat, lon, lat_min, lon_min, lat_max, lon_max):
    num_dislat = int((lat_max - lat_min + 0.00001) / 0.008)
    dis_lat = int((lat - lat_min) / 0.008)
    dis_lon = int((lon - lon_min) / 0.010)

    return dis_lat + dis_lon * num_dislat


def read_P(filename):
    return np.genfromtxt(filename, delimiter = ',')


def read_traj(filename, lat_min, lat_max, lon_min, lon_max, num_loc):
    traj_set = dict({})
    init_time = time.mktime(time.strptime('2011-12-30 23:50:00', '%Y-%m-%d %H:%M:%S'))

    with open(filename, 'r') as f:
        for u_str, lat_str, lon_str, time_str in csv.reader(f):
            u = int(u_str)
            tstamp = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
            lat = float(lat_str)
            lon = float(lon_str)
            if lat < lat_min or lat >= lat_max or lon < lon_min or lon >= lon_max:
                continue
            lidx = get_loc_idx(lat, lon, lat_min, lon_min, lat_max, lon_max)

            tidx = int(tstamp - init_time) / 3600
            if tidx < 0 or tidx >= 48 or lidx < 0 or lidx >= num_loc:
                continue

            if u not in traj_set:
                traj_set[u] = []

            traj_set[u].append((lidx, time_str))

    return traj_set


def simple_transfer(traj_t, P):
    traj_o = dict({})
    for u in traj_t:
        traj_o[u] = []
        for lidx, time_str in traj_t[u]:
            p_l = P[lidx, :]
            lidx_o = np.random.multinomial(1, p_l).argmax()
            traj_o[u].append([lidx_o,time_str])

    return traj_o


#  def mrf_smoothing(traj_o, traj_t, P):
    #  # prepare distance matrix
    #  distance_tokyo = np.zeros([num_loc_t,num_loc_t])
    #  distance_osaka = np.zeros([num_loc_o,num_loc_o])

    #  for i in xrange(num_loc_t):
        #  for j in xrange(i):
            #  distance_tokyo[i,j] = distance_tokyo[j,i] = ((i % num_dislat_t - j % num_dislat_t) ** 2 + (i / num_dislat_t - j / num_dislat_t) ** 2) ** 0.5

    #  for i in xrange(num_loc_o):
        #  for j in xrange(i):
            #  distance_osaka[i,j] = distance_osaka[j,i] = ((i % num_dislat_o - j % num_dislat_o) ** 2 + (i / num_dislat_o - j / num_dislat_o) ** 2) ** 0.5

    #  # Gibbs iteration
    #  for u in traj_o:
        #  if len(traj_o[u]) < 3:
            #  continue
        #  print 'Resample {}'.format(u)
        #  for i in xrange(MAX_GIBBS_ITERATION * len(traj_o[u])):
            #  t = np.random.randint(len(traj_o[u]))
            #  if t == 0:
                #  l_cur_t = traj_t[u][0][0]
                #  l_pro_t = traj_t[u][1][0]
                #  dist_t = distance_tokyo[l_cur_t, l_pro_t]
                #  l_pro_o = traj_o[u][1][0]
                #  dist_o_vec = distance_osaka[l_pro_o, :]
                #  spatial_smooth = np.exp( -(((dist_o_vec - dist_t) / (dist_t + 0.01)) ** 2) )
                #  p_l = P[l_cur_t, :] * spatial_smooth
                #  p_l /= np.sum(p_l)
                #  l_cur_o = np.random.multinomial(1, p_l).argmax()
                #  traj_o[u][0][0] = l_cur_o
            #  elif t == len(traj_o[u]) - 1:
                #  l_cur_t = traj_t[u][-1][0]
                #  l_pre_t = traj_t[u][-2][0]
                #  dist_t = distance_tokyo[l_cur_t, l_pre_t]
                #  l_pre_o = traj_o[u][-2][0]
                #  dist_o_vec = distance_osaka[l_pre_o, :]
                #  spatial_smooth = np.exp( -(((dist_o_vec - dist_t) / (dist_t + 0.01)) ** 2) )
                #  p_l = P[l_cur_t, :] * spatial_smooth
                #  p_l /= np.sum(p_l)
                #  l_cur_o = np.random.multinomial(1, p_l).argmax()
                #  traj_o[u][-1][0] = l_cur_o
            #  else:
                #  l_cur_t = traj_t[u][t][0]
                #  l_pro_t = traj_t[u][t+1][0]
                #  l_pre_t = traj_t[u][t-1][0]
                #  dist_t_pro = distance_tokyo[l_cur_t, l_pro_t]
                #  dist_t_pre = distance_tokyo[l_cur_t, l_pre_t]
                #  l_pro_o = traj_o[u][t+1][0]
                #  l_pre_o = traj_o[u][t-1][0]
                #  dist_o_pro_vec = distance_osaka[l_pro_o, :]
                #  dist_o_pre_vec = distance_osaka[l_pre_o, :]
                #  spatial_smooth = np.exp( -(((dist_o_pro_vec - dist_t_pro) / (dist_t_pro + 0.01)) ** 2 + ((dist_o_pre_vec - dist_t_pre) / (dist_t_pre + 0.01)) ** 2))
                #  p_l = P[l_cur_t, :] * spatial_smooth
                #  p_l /= np.sum(p_l)
                #  l_cur_o = np.random.multinomial(1, p_l).argmax()
                #  traj_o[u][t][0] = l_cur_o

    #  return traj_o


def get_random_coordinates(lidx_o):
    num_dislat = int((lat_max_o - lat_min_o + 0.00001) / 0.008)
    dis_lat = lidx_o % num_dislat
    dis_lon = lidx_o / num_dislat
    lat = lat_min_o + 0.008 * dis_lat + 0.002 + 0.004 * np.random.ranf()
    lon = lon_min_o + 0.010 * dis_lon + 0.0025 + 0.005 * np.random.ranf()
    return lat, lon


def output_simulated(traj_o, filename):
    with open(filename, 'w')  as f:
        for u in traj_o:
            for lidx_o,time_str in traj_o[u]:
                lat, lon = get_random_coordinates(lidx_o)
                f.write('{},{},{},{}\n'.format(u, lat, lon, time_str))


def main():
    P = read_P('./dp_rst/P_ITER1000.csv')
    P /= np.sum(P, axis=0)
    print P.shape
    P = P.T
    traj_t = read_traj('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/2011newyear.csv', lat_min_t, lat_max_t, lon_min_t, lon_max_t, num_loc_t)
    traj_o = simple_transfer(traj_t, P)
    #  traj_o = mrf_smoothing(traj_o, traj_t, P)
    output_simulated(traj_o, './simulated_osaka_newyear_simple.csv')


if __name__ == '__main__':
    main()
