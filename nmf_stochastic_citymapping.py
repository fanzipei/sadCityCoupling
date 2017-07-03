#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import csv
from scipy.sparse import lil_matrix


num_u = 200
num_loc_t = 1850
num_loc_o = 2000
loc_ratio = 2000.0 / 1850.0
num_day = 5
num_time = 72
num_iter = 100
alpha = 0.001
beta = 1.0
miu = 0.004


def load_sparse_matrix(filename, num_loc):
    Ytd = [np.zeros([num_u, num_loc], dtype=np.float) for j in xrange(num_time)]
    with open(filename, 'r') as f:
        for uid_str, uidx_str, lidx_str, tidx_str in csv.reader(f):
            uidx = int(uidx_str)
            lidx = int(lidx_str)
            tidx = int(tidx_str) / 2
            Ytd[tidx][(uidx, lidx)] += 1.0
            Ytd[(tidx+1)%num_time][(uidx, lidx)] += 0.5
            Ytd[(tidx-1)%num_time][(uidx, lidx)] += 0.5
            Ytd[(tidx+2)%num_time][(uidx, lidx)] += 0.25
            Ytd[(tidx-2)%num_time][(uidx, lidx)] += 0.25
            Ytd[(tidx+3)%num_time][(uidx, lidx)] += 0.125
            Ytd[(tidx-3)%num_time][(uidx, lidx)] += 0.125

    return Ytd


def nmf_multiplitive_iteration(Yt, Yo, Xt, Xo):
    P = np.random.ranf([num_loc_t, num_loc_o]) / (0.5 * (num_loc_o * num_loc_t) ** 0.5)
    A = [0.001 * np.random.ranf([num_u, num_u]) for i in xrange(num_day)]
    for i in xrange(num_iter):

        for d in xrange(num_day):
            upper = np.zeros([num_u, num_u]) + 2 * miu
            lower = alpha * A[d] + miu * A[d].dot(np.ones([num_u, num_u])) + miu * np.sum(A[d], axis=0)
            for t in xrange(num_time):
                tmp = Yt[d][t].dot(P)
                upper += Yo[d][t].dot(tmp.T)
                lower += A[d].dot(tmp).dot(tmp.T)
            A[d] *= upper / lower
            print 'A{} updated'.format(d)

        #  print 'beta * Xt.dot(Xo.T) = {}'.format(np.sum(beta * Xt.dot(Xo.T)))
        #  print 'alpha * P = {}'.format(np.sum(alpha * P))
        #  print 'beta * (Xt.dot(Xt.T)).dot(P) = {}'.format(np.sum(beta * (Xt.dot(Xt.T)).dot(P)))
        #  print 'miu * P.dot(1) = {}'.format(np.sum(miu * P.dot(np.ones([num_loc_o, num_loc_o]))))
        upper = beta * Xt.dot(Xo.T) + miu
        lower = alpha + beta * (Xt.dot(Xt.T)).dot(P) +  miu * P.dot(np.ones([num_loc_o, num_loc_o]))
        #  upper_data = np.zeros([num_loc_t, num_loc_o])
        #  lower_data = np.zeros([num_loc_t, num_loc_o])
        for d in xrange(num_day):
            for t in xrange(num_time):
                tmp = A[d].dot(Yt[d][t])
                upper += tmp.T.dot(Yo[d][t])
                #  upper_data += tmp.T.dot(Yo[d][t])
                lower += tmp.T.dot(tmp.dot(P))
                #  lower_data += tmp.T.dot(tmp.dot(P))
        #  print 'lower data = {}'.format(np.sum(lower_data))
        #  print 'upper data = {}'.format(np.sum(upper_data))
        P *= upper / lower
        print 'P updated'

        yield i, P, A


def main():
    Yt = [[] for i in xrange(num_day)]
    Yo = [[] for i in xrange(num_day)]
    for i in xrange(num_day):
        print 'Read {}th files'.format(i+1)
        Yt[i] = load_sparse_matrix('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/traj200/201206{:02d}.csv'.format(i+1), num_loc_t)
        Yo[i] = load_sparse_matrix('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/traj200/201206{:02d}.csv'.format(i+1), num_loc_o)

    Xo = np.genfromtxt('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/aggregated_mobilitygraph_large/node.csv', delimiter=',', dtype=np.float)
    Xt = np.genfromtxt('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/aggregated_mobilitygraph_large/node.csv', delimiter=',', dtype=np.float)
    Xo /= np.sum(Xo, axis=0)
    Xt /= np.sum(Xt, axis=0)

    for i, P, A in nmf_multiplitive_iteration(Yt, Yo, Xt, Xo):
        print 'Iteration {}'.format(i)
        np.savetxt('./nmf_rst/P_ITER{}_undoubly.csv'.format(i), P, delimiter=',')
        for d in xrange(num_day):
            np.savetxt('./nmf_rst/A_ITER{}_DAY{}.csv'.format(i, d+1), A[d], delimiter=',')


if __name__ == '__main__':
    main()
