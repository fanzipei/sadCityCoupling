#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import csv
import random
from munkres import Munkres

num_day = 61
num_time = 72
num_u = 250
num_loc_o = 2000
num_loc_t = 1850
max_iter = 200
gamma = 0.005


def load_data(filename, num_loc, is_gaussian):
    user_traj = dict({})
    with open(filename, 'r') as f:
        for uidx_str, lidx_str, tidx_str in csv.reader(f):
            uidx = int(uidx_str)
            lidx = int(lidx_str)
            tidx = int(tidx_str)
            if uidx not in user_traj:
                user_traj[uidx] = []
            user_traj[uidx].append((lidx, tidx))
    for uidx in user_traj:
        if len(user_traj[uidx]) < 5:
            del user_traj[uidx]

    return user_traj


def load_sparse_matrix(data_batch, num_loc, is_gaussian):
    Ytd = np.zeros([num_time, num_u, num_loc], dtype=np.float) + 0.01
    for uidx in xrange(data_batch):
        for lidx_str, tidx_str in data_batch[uidx]:
            lidx = int(lidx_str)
            tidx = int(tidx_str) / 2
            Ytd[(tidx, uidx, lidx)] += 1.0
            if is_gaussian:
                Ytd[((tidx+1)%num_time, uidx, lidx)] += 0.5
                Ytd[((tidx-1)%num_time, uidx, lidx)] += 0.5
                Ytd[((tidx+2)%num_time, uidx, lidx)] += 0.25
                Ytd[((tidx-2)%num_time, uidx, lidx)] += 0.25
                Ytd[((tidx+3)%num_time, uidx, lidx)] += 0.125
                Ytd[((tidx-3)%num_time, uidx, lidx)] += 0.125
                Ytd[((tidx+4)%num_time, uidx, lidx)] += 0.0625
                Ytd[((tidx-4)%num_time, uidx, lidx)] += 0.0625

    if is_gaussian:
        norm = np.sum(Ytd, axis=2)
        for i in xrange(num_loc):
            Ytd[:, :, i] /= norm

    return Ytd


def get_matching(score):
    score_list = list(-score)
    m = Munkres()
    indexes = m.compute(score_list)
    return indexes


def dirichlet_process(P, XO, XT):
    data_t = []
    data_o = []
    for m in xrange(6, 8):
        for d in xrange(1, 32):
            if m == 6 and d == 31:
                continue
            filename_t = '/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/discretized/2012{:02d}{:02d}.csv'.format(m, d)
            print 'Reading {}'.format(filename_t)
            data_t.append(load_data(filename_t, num_loc_t, True))
            filename_o = '/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/discretized/2012{:02d}{:02d}.csv'.format(m, d)
            print 'Reading {}'.format(filename_o)
            data_o.append(load_data(filename_o, num_loc_o, False))


    for i in xrange(max_iter):
        d = np.random.randint(num_day)
        data_t_batch = random.sample(data_t[d].values(), num_u)
        data_o_batch = random.sample(data_o[d].values(), num_u)
        Ytd = load_sparse_matrix(data_t_batch, num_loc_t, True)
        Yod = load_sparse_matrix(data_o_batch, num_loc_o, False)
        Yoe = np.log(Ytd.dot(P.T) + 1e-30)
        score = np.zeros([num_u, num_u])
        print 'Building Score Matrix'
        for uo in xrange(num_u):
            for ut in xrange(num_u):
                score[uo, ut] = np.sum(Yod[:, uo, :] * Yoe[:, ut, :])
        print 'Score Matrix Complete'
        indexes = get_matching(score)
        print 'Find out best matching complete'
        dP = np.zeros([num_loc_o, num_loc_t])
        for uo, ut in indexes:
            dP += Yod[:, uo, :].T.dot(Ytd[:, ut, :])

        dX = XO - P.dot(XT)
        dPX = dP.dot(XT)
        wdP = dX.dot(dPX.T) / ((dX.dot(dX.T) * dPX.dot(dPX.T)) ** 0.5) + 1
        P += gamma * dP * wdP
        P /= np.sum(P, axis=0)
        print 'Update P complete'

        yield i, P, dP


def main():
    P = np.genfromtxt('./P_tokyo2osaka.csv', delimiter=',')
    XO = np.genfromtxt('/media/fan/HDPC-UT/ZDC/TrainingForMapping/node_osaka.csv', delimiter=',', dtype=np.float)
    XT = np.genfromtxt('/media/fan/HDPC-UT/ZDC/TrainingForMapping/node_tokyo.csv', delimiter=',', dtype=np.float)
    XO /= np.sum(XO, axis=0)
    XT /= np.sum(XT, axis=0)
    print P.shape
    for i, P, dP in dirichlet_process(P, XO, XT):
        print 'Iteration {}'.format(i)
        np.savetxt('./dp_rst/P_.csv', P, delimiter=',')
        # np.savetxt('./dp_rst/dP_ITER{}.csv'.format(i), dP, delimiter=',')


if __name__ == '__main__':
    main()
