#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import csv


K = 4
ita = 1e-6
gamma = 1e-5
alpha = 10.0
epsilon = 1e-10
BATCH_SIZE = 10
MAX_TIME = 2880
NUM_LOC_A = 1850
NUM_LOC_B = 2000


def load_graph(filename,NUM_LOC):
    G = np.zeros([NUM_LOC,NUM_LOC],np.float)
    with open(filename,'r') as f:
        for loc_ori_str,loc_des_str,cnt_str in csv.reader(f):
            loc_ori = int(loc_ori_str)
            loc_des = int(loc_des_str)
            cnt = float(cnt_str)
            if loc_ori == loc_des:
                cnt /= 5.0
            G[(loc_ori,loc_des)] = cnt

    return G


def get_distance_matrix(num_loc, num_lat, num_lon):
    DIS = np.zeros([num_loc, num_loc])
    for i in xrange(num_loc):
        for j in xrange(i):
            dis_lat_i = i % num_lat
            dis_lon_i = i / num_lat
            dis_lat_j = j % num_lon
            dis_lon_j = j / num_lon
            DIS[i, j] = DIS[j, i] = ((dis_lat_i - dis_lat_j) ** 2 + (dis_lon_i - dis_lon_j) ** 2) ** 0.5

    return DIS


def optimize(path_A, path_B, MAX_ITER):
    #  DA = get_distance_matrix(NUM_LOC_A, 37, 50)
    #  DB = get_distance_matrix(NUM_LOC_B, 50, 40)
    P = [2.0 * np.random.ranf([NUM_LOC_B, NUM_LOC_A]) / NUM_LOC_B  for k in xrange(K)]

    for i in xrange(MAX_ITER):
        #  lambda_dis = np.sum(DA) / np.sum(DB)
        #  DB_SCALED = lambda_dis * DB
        #  print 'Sum of DA = {}'.format(np.sum(DA))
        #  print 'lambda_dis = {}'.format(lambda_dis)

        for k_dev in xrange(K):

            #  dP = alpha * P[k_dev]
            dP = np.zeros([NUM_LOC_B, NUM_LOC_A])

            for b in xrange(BATCH_SIZE):
                idx = np.random.randint(MAX_TIME)
                print 'Batch {}'.format(b)
                filename_A = path_A + 'graph_H{}_30.csv'.format(idx)
                filename_B = path_B + 'graph_H{}_30.csv'.format(idx)
                print 'Reading ' + filename_A
                GA = load_graph(filename_A,NUM_LOC_A)
                print 'Sum of GA: {}'.format(np.sum(GA))
                print 'Reading ' + filename_B
                GB = load_graph(filename_B,NUM_LOC_B)
                print 'Sum of GB: {}'.format(np.sum(GB))

                lambda_graph = np.sum(GA) / np.sum(GB)
                GB = K * lambda_graph * GB
                print 'lambda_graph = {}'.format(lambda_graph)

                PGAT = P[k_dev].dot(GA.T)
                PGA = P[k_dev].dot(GA)
                dP -= GB.dot(PGAT) + GB.T.dot(PGA)
                for k_itr in xrange(K):
                    print 'The {}th component'.format(k_itr)
                    dP += P[k_itr].dot((GA.dot(P[k_itr].T)).dot(PGAT) + GA.T.dot(P[k_itr].T).dot(PGA))

            #  PDA = P[k_dev].dot(DA)
            #  dP_D = -DB_SCALED.dot(PDA)
            #  for k_itr in xrange(K):
                #  dP_D += P[k_itr].dot(DA.dot(P[k_itr].T)).dot(PDA)
            #  dP += gamma * dP_D

            dP += 1000.0 * (P[k_dev].dot(np.ones([NUM_LOC_A, NUM_LOC_A])) + np.sum(P[k_dev], axis=0) - 2)
            P[k_dev] -= ita * dP
            P[k_dev][P[k_dev] < epsilon] = epsilon

            yield i, k_dev, P[k_dev]


def main():
    for it, k, P in optimize('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/mobilitygraph_large_new/','/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/mobilitygraph_large_new/', 1000):
        print 'Iteration {}, the {}th component'.format(it, k)
        np.savetxt('./PK5B10ITA0001GAMMA01ALPHA01/P_K{}_ITER{}.csv'.format(k, it), P, delimiter=',')

if __name__ == '__main__':
    main()
