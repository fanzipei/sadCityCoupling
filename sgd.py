#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import csv

TMAX = 2880
INTERVAL = 3
NUM_LOC_A = 7500
NUM_LOC_B = 8000
ita = 0.00005
alpha = 0.02
beta = 0.5
MAXITER = 100


def positive_constrain( mat ):
    for x in np.nditer( mat , op_flags=['readwrite']):
        x[...] = max( x , 0.000000000000001 )

def cal_sgd(GA, GB, W):
    dw0 = (W.dot(GA.dot(W.T)) - GB).dot(W.dot(GA.T)) + (W.dot(GA.T.dot(W.T)) - GB.T).dot(W.dot(GA)) + alpha
    return dw0


def load_graph(filename,NUM_LOC):
    G = np.zeros([NUM_LOC,NUM_LOC],np.int32)
    with open(filename,'r') as f:
        for loc_ori_str,loc_des_str,cnt_str in csv.reader(f):
            loc_ori = int(loc_ori_str)
            loc_des = int(loc_des_str)
            # if loc_ori == loc_des:
                # continue
            cnt = int(cnt_str)
            G[(loc_ori,loc_des)] = cnt

    return G


def optimize(path_A,path_B,MAX_ITER):
    W = np.random.ranf([NUM_LOC_B,NUM_LOC_A])
    W /= np.sum(W,axis=0)
    pre_dw = np.zeros([NUM_LOC_B,NUM_LOC_A],np.float)
    for i in xrange(MAXITER):
        print 'Iteration {}'.format(i+1)
        t = np.random.randint(TMAX)
        itv = np.random.randint(INTERVAL) * 10 + 10
        filename_A = path_A + 'graph_H{}_{}.csv'.format(t,itv)
        filename_B = path_B + 'graph_H{}_{}.csv'.format(t,itv)
        print 'Reading ' + filename_A
        GA = load_graph(filename_A,NUM_LOC_A)
        print 'Reading ' + filename_B
        GB = load_graph(filename_B,NUM_LOC_B)
        dw = ita * cal_sgd(GA,GB,W) + beta * pre_dw
        W -= dw
        W /= np.sum(W,axis=0)
        positive_constrain(W)
        # print W[0,:]
        # print np.sum(W,axis=0)
        pre_dw = dw

    return W


def main():
    W = optimize('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/mobilitygraph/',\
            '/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/mobilitygraph/', 10000)
    np.savetxt('W_A002B05ITA000005ITR200_NORMALIZED.csv', W, delimiter=',')

if __name__ == '__main__':
    main()
