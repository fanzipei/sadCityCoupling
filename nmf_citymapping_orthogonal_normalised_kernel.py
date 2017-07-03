#!/usr/bin/env python
# encoding: utf-8

import csv
import time
import numpy as np
import datetime
from scipy.sparse import lil_matrix

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

# Constants
alpha = 100.0
beta = 100.0
gamma = 500.0
epsilon = 1e-30

K = 100


def get_loc_idx(lat, lon, lat_min, lon_min, lat_max, lon_max):
    num_dislat = int((lat_max - lat_min + 0.00001) / 0.008)
    dis_lat = int((lat - lat_min) / 0.008)
    dis_lon = int((lon - lon_min) / 0.010)

    return dis_lat + dis_lon * num_dislat


def load_traj(filename, lat_min, lon_min, lat_max, lon_max, num_loc):
    print 'Load file:' + filename
    traj_set = dict({})

    init_time = time.mktime(time.strptime('2012-05-31 23:50:00', '%Y-%m-%d %H:%M:%S'))

    with open(filename, 'r') as f:
        for u_str, time_str, lat_str, lon_str in csv.reader(f):
            u = int(u_str)
            tstamp = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
            lat = float(lat_str)
            lon = float(lon_str)
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


def get_sparse_tensor(traj, num_loc, outfilename, ratio):
    num_u = len(traj)
    usr_idx = dict({})
    Y = [lil_matrix((num_u, num_loc), dtype=np.float) for t in xrange(144)]
    uidx = 0

    # tf-idf
    # visit_cnt = np.zeros(num_loc, np.float)
    # user_visit = dict({})

    # for u in traj:
        # usr_idx[u] = uidx
        # user_visit[u] = set([])
        # for lidx, tidx in traj[u]:
            # visit_cnt[lidx] += 1
            # user_visit[u].add(lidx)
        # uidx += 1
    # for u in traj:
        # for lidx, tidx in traj[u]:
            # Y[tidx][(usr_idx[u], lidx)] += ratio * 1000.0 / visit_cnt[lidx] * (np.log(num_loc) - np.log(len(user_visit[u])))
            # Y[(tidx + 1) % 144][(usr_idx[u], lidx)] += ratio * 500.0 / visit_cnt[lidx] * (np.log(num_loc) - np.log(len(user_visit[u])))
            # Y[tidx - 1][(usr_idx[u], lidx)] += ratio * 500.0 / visit_cnt[lidx] * (np.log(num_loc) - np.log(len(user_visit[u])))
            # Y[(tidx + 2) % 144][(usr_idx[u], lidx)] += ratio * 250.0 / visit_cnt[lidx] * (np.log(num_loc) - np.log(len(user_visit[u])))
            # Y[tidx - 2][(usr_idx[u], lidx)] += ratio * 250.0 / visit_cnt[lidx] * (np.log(num_loc) - np.log(len(user_visit[u])))
            # Y[(tidx + 3) % 144][(usr_idx[u], lidx)] += ratio * 125.0 / visit_cnt[lidx] * (np.log(num_loc) - np.log(len(user_visit[u])))
            # Y[tidx - 3][(usr_idx[u], lidx)] += ratio * 125.0 / visit_cnt[lidx] * (np.log(num_loc) - np.log(len(user_visit[u])))

    for u in traj:
        usr_idx[u] = uidx
        for lidx, tidx in traj[u]:
            Y[tidx][(usr_idx[u], lidx)] += ratio
            Y[(tidx + 1) % 144][(usr_idx[u], lidx)] += ratio * 0.5
            Y[tidx - 1][(usr_idx[u], lidx)] += ratio * 0.5
            Y[(tidx + 2) % 144][(usr_idx[u], lidx)] += ratio * 0.25
            Y[tidx - 2][(usr_idx[u], lidx)] += ratio * 0.25
            Y[(tidx + 3) % 144][(usr_idx[u], lidx)] += ratio * 0.125
            Y[tidx - 3][(usr_idx[u], lidx)] += ratio * 0.125
            Y[(tidx + 4) % 144][(usr_idx[u], lidx)] += ratio * 0.0625
            Y[tidx - 4][(usr_idx[u], lidx)] += ratio * 0.0625
        uidx += 1

    # Output User index
    with open(outfilename, 'w') as f:
        for u in usr_idx:
            f.write('{},{}\n'.format(u, usr_idx[u]))

    return Y, num_u


def nmf_multiplitive_iteration(Y_t, Y_o, num_u_t, num_u_o, max_iter):
    Ao = np.random.ranf([num_u_o, K]) / (0.5 * (K * num_u_t) ** 0.5)
    At = np.random.ranf([num_u_t, K]) / (0.5 * (K * num_u_t) ** 0.5)
    P = np.random.ranf([num_loc_t, num_loc_o]) / (num_loc_t * 0.5)

    for it in xrange(1, max_iter + 1):
        upper = np.zeros([num_u_o, K], np.float)
        lower = np.zeros([num_u_o, K], np.float)

        for i in xrange(144):
            print 'i:{}'.format(i)
            upper += Y_o[i].dot(P.T.dot(Y_t[i].T.dot(At)))
            tmp = At.T.dot(Y_t[i].dot(P))
            lower += Ao.dot(tmp.dot(tmp.T))

        Ao *= upper / (lower + alpha * Ao)
        Ao[Ao < epsilon] = epsilon
        print 'Ao updated'

        upper = np.zeros([num_u_t, K], np.float)
        lower = np.zeros([num_u_t, K], np.float)

        for i in xrange(144):
            print 'i:{}'.format(i)
            upper += Y_t[i].dot(P.dot(Y_o[i].T.dot(Ao)))
            tmp = Y_t[i].dot(P)
            lower += tmp.dot(tmp.T.dot(At).dot(Ao.T.dot(Ao)))

        At *= upper / (lower + beta * At)
        At[At < epsilon] = epsilon
        print 'At updated'

        upper = np.zeros([num_loc_t, num_loc_o], np.float)
        lower = np.zeros([num_loc_t, num_loc_o], np.float)

        for i in xrange(144):
            print 'i:{}'.format(i)
            upper += Y_t[i].T.dot(At).dot((Y_o[i].T.dot(Ao)).T)
            # nonorthogonal
            tmp = Y_t[i].T.dot(At)
            lower += tmp.dot(Ao.T.dot(Ao).dot(tmp.T).dot(P))
            # orthogonal
            # lower += P.dot(Y_o[i].T.dot(Ao)).dot((At.T.dot(Y_t[i])).dot(P))
            # lower += P.dot(Y_o[i].T.dot(Ao)).dot((Y_t[i].T.dot(At)).T.dot(P))

        P *= upper / (lower + gamma * P)
        P[P < epsilon] = epsilon
        print 'P updated'

        P = (P.T / np.sum(P, axis=1)).T
        print 'Normalization'

        yield it, Ao, At, P


def cnt_traj(traj_set):
    cnt = 0.0
    for traj in traj_set.values():
        cnt += len(traj)

    return cnt


def main():
    traj_t = load_traj('/home/fan/ZDC/TrainingForMapping/tokyo/20120601.csv', lat_min_t, lon_min_t, lat_max_t, lon_max_t, num_loc_t)
    traj_o = load_traj('/home/fan/ZDC/TrainingForMapping/osaka/20120601.csv', lat_min_o, lon_min_o, lat_max_o, lon_max_o, num_loc_o)
    traj_t = trim_traj(traj_t)
    traj_o = trim_traj(traj_o)
    print 'Len Tokyo:{}'.format(len(traj_t))
    print 'Len Osaka:{}'.format(len(traj_o))
    cnt_t = cnt_traj(traj_t)
    cnt_o = cnt_traj(traj_o)
    print 'Point Tokyo:{}'.format(cnt_t)
    print 'Point Osaka:{}'.format(cnt_o)
    Y_t, num_u_t = get_sparse_tensor(traj_t, num_loc_t, 'user_index_tokyo.csv', cnt_o / cnt_t)
    del traj_t
    print 'Sparse Matrix form of trajectory for tokyo'
    Y_o, num_u_o = get_sparse_tensor(traj_o, num_loc_o, 'user_index_osaka.csv', 1.0)
    del traj_o
    print 'Sparse Matrix form of trajectory for osaka'
    for it, Ao, At, P in nmf_multiplitive_iteration(Y_t, Y_o, num_u_t, num_u_o, 50):
        print 'Iteration {} completed.'.format(it)
        print datetime.datetime.now()
        np.savetxt('./K100_ALPHA100_BETA100_GAMMA500_scaled_normalised_nonorthogonal_kernel/Ao_ITER{}_K100_ALPHA100_BETA100_GAMMA_500_ORTHO.csv'.format(it), Ao, delimiter=',')
        np.savetxt('./K100_ALPHA100_BETA100_GAMMA500_scaled_normalised_nonorthogonal_kernel/At_ITER{}_K100_ALPHA100_BETA100_GAMMA_500_ORTHO.csv'.format(it), At, delimiter=',')
        np.savetxt('./K100_ALPHA100_BETA100_GAMMA500_scaled_normalised_nonorthogonal_kernel/P_ITER{}_K100_ALPHA100_BETA100_GAMMA_500_ORTHO.csv'.format(it), P, delimiter=',')


if __name__ == '__main__':
    main()