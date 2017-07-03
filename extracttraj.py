#!/usr/bin/env python
# encoding: utf-8

import csv
import time
import numpy as np

# Tokyo
lat_min_t = 35.5
lat_max_t = 35.8
lon_min_t = 139.4
lon_max_t = 139.9
num_loc_t = 7500
# Osaka
lat_min_o = 34.45
lat_max_o = 34.85
lon_min_o = 135.3
lon_max_o = 135.7
num_loc_o = 8000

# Constants
K = 100
NUM_ITER = 50
alpha = 1.0
beta = 10.0


def get_loc_idx(lat,lon,lat_min,lon_min,lat_max,lon_max):
    num_dislat = int( ( lat_max - lat_min + 0.00001 )/0.004 )
    dis_lat = int( ( lat - lat_min )/0.004 )
    dis_lon = int( ( lon - lon_min )/0.005 )

    return dis_lat + dis_lon*num_dislat


def load_traj(filename,lat_min,lon_min,lat_max,lon_max):
    print 'Load file:' + filename
    traj_set = dict({})

    init_time = time.mktime(time.strptime('2012-05-31 23:50:00','%Y-%m-%d %H:%M:%S'))

    with open(filename,'r') as f:
        for u_str,time_str,lat_str,lon_str in csv.reader(f):
            u = int(u_str)
            tstamp = time.mktime(time.strptime(time_str,'%Y-%m-%d %H:%M:%S'))
            lat = float(lat_str)
            lon = float(lon_str)
            lidx = get_loc_idx(lat,lon,lat_min,lon_min,lat_max,lon_max)
            tidx = int(tstamp - init_time) / 1800

            if u not in traj_set:
                traj_set[u] = []

            traj_set[u].append((lidx,tidx))

    return traj_set


def trim_traj(traj):
    return dict((k,v) for k,v in traj.items() if len(v) >= 10 )


def conditional_distribution(PorPT, traj, geo_dis, geo_stat, n_k):
    p_k = np.ones(K)
    for lidx,tidx in traj:
        p_k_step = ( geo_dis[:,tidx,:].T + alpha ).dot(PorPT[:,lidx])
        p_k_step /= geo_stat[tidx]
        p_k *= p_k_step
    p_k *= n_k + beta
    p_k /= np.sum(p_k)

    return p_k


def city_matching(traj_t, traj_o):
    topic_alloc_t = dict({})
    topic_alloc_o = dict({})
    geo_dis_t = np.zeros([num_loc_t,48,K],np.int32)
    geo_dis_o = np.zeros([num_loc_o,48,K],np.int32)
    P = np.zeros([num_loc_o,num_loc_t],np.int32)
    nk_t = np.zeros(K,np.int32)
    nk_o = np.zeros(K,np.int32)

    # Initialize
    for u in traj_t:
        k = topic_alloc_t[u] = np.random.randint(K)
        for lidx,tidx in traj_t[u]:
            geo_dis_t[(lidx,tidx,k)] += 1
            nk_t[k] += 1

    for u in traj_o:
        k = topic_alloc_o[u] = np.random.randint(K)
        for lidx,tidx in traj_o[u]:
            geo_dis_o[(lidx,tidx,k)] += 1
            P[lidx,:] += geo_dis_t[:,tidx,k]
            nk_o[k] += 1

    geo_stat_t = np.sum(geo_dis_t,axis=0)
    geo_stat_o = np.sum(geo_dis_o,axis=0)

    # Iteration
    for i in xrange(NUM_ITER):
        print 'Iteration {}'.format(i+1)
        for u in traj_t:
            k_old = topic_alloc_t[u]
            # Eliminate the effect
            for lidx,tidx in traj_t[u]:
                geo_dis_t[(lidx,tidx,k_old)] -= 1
                geo_stat_t[(tidx,k_old)] -= 1
                P[:,lidx] -= geo_dis_o[:,tidx,k]
                nk_t[k_old] -= 1
            # Sample a new k
            p_k = conditional_distribution(P,traj_t[u],geo_dis_o,geo_stat_o,nk_t)
            k_new = np.random.multinomial(1,p_k).argmax()
            topic_alloc_t[u] = k_new
            # Update
            for lidx,tidx in traj_t[u]:
                geo_dis_t[(lidx,tidx,k_new)] += 1
                geo_stat_t[(tidx,k_new)] += 1
                P[:,lidx] += geo_dis_o[:,tidx,k]
                nk_t[k_new] += 1

        for u in traj_o:
            k_old = topic_alloc_o[u]
            # Eliminate the effect
            for lidx,tidx in traj_o[u]:
                geo_dis_o[(lidx,tidx,k_old)] -= 1
                geo_stat_o[(tidx,k_old)] -= 1
                P[:,lidx] -= geo_dis_t[:,tidx,k]
                nk_o[k_old] -= 1
            # Sample a new k
            p_k = conditional_distribution(P.T,traj_o[u],geo_dis_t,geo_stat_t,nk_o)
            k_new = np.random.multinomial(1,p_k).argmax()
            topic_alloc_o[u] = k_new
            # Update
            for lidx,tidx in traj_o[u]:
                geo_dis_o[(lidx,tidx,k_new)] += 1
                geo_stat_o[(tidx,k_new)] += 1
                P[:,lidx] += geo_dis_t[:,tidx,k]
                nk_o[k_old] += 1

    return P,topic_alloc_t,topic_alloc_o,geo_dis_t,geo_dis_o


def main():
    traj_t = load_traj('/media/fan/HDPC-UT2/ZDC/TrainingForMapping/tokyo/20120601.csv',lat_min_t,lon_min_t,lat_max_t,lon_max_t)
    traj_o = load_traj('/media/fan/HDPC-UT2/ZDC/TrainingForMapping/osaka/20120601.csv',lat_min_o,lon_min_o,lat_max_o,lon_max_o)
    traj_t = trim_traj(traj_t)
    traj_o = trim_traj(traj_o)
    print 'Len Tokyo:{}'.format(len(traj_t))
    print 'Len Osaka:{}'.format(len(traj_o))
    # traj_t = transfer_timeslot_traj(traj_t)
    # traj_o = transfer_timeslot_traj(traj_o)
    P,topic_alloc_t,topic_alloc_o,geo_dis_t,geo_dis_o = city_matching(traj_t,traj_o)
    np.savetxt('W_GIBBS_ITER50_ALPHA1_K100.csv', P, delimiter=',')


if __name__ == '__main__':
    main()
