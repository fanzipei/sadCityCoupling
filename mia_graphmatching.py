#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import csv


K = 5
alpha = 1.0
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
            #  if loc_ori == loc_des:
                #  cnt /= 5.0
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
    DA = get_distance_matrix(NUM_LOC_A, 37, 50)
    DB = get_distance_matrix(NUM_LOC_B, 50, 40)
    P = [np.random.ranf([NUM_LOC_B, NUM_LOC_A]) for k in xrange(K)]
    for k in xrange(K):
        P[k] /= np.sum(P[k], axis=0)

    for i in xrange(MAX_ITER):
        #  PDAP = np.zeros([NUM_LOC_B, NUM_LOC_B])
        #  for k in xrange(K):
            #  PDAP += P[k].dot(DA).dot(P[k].T)
        #  lambda_dis = np.sum(PDAP * DB) / np.sum(DB * DB)
        lambda_dis = np.sum(DA) / np.sum(DB)
        DB_SCALED = lambda_dis * DB
        print 'lambda_dis = {}'.format(lambda_dis)

        P_new = [np.zeros([NUM_LOC_B, NUM_LOC_A]) for k in xrange(K)]
        for k_dev in xrange(K):
            upper = np.zeros([NUM_LOC_B, NUM_LOC_A])
            lower = np.zeros([NUM_LOC_B, NUM_LOC_A]) + alpha

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

                #  PGAP = np.zeros([NUM_LOC_B, NUM_LOC_B])
                #  for k in xrange(K):
                    #  PGAP += P[k].dot(GA).dot(P[k].T)
                #  print 'Sum of PGAP: {}'.format(np.sum(PGAP))
                #  lambda_graph = np.sum(PGAP * GB) / np.sum(GB * GB)
                lambda_graph = np.sum(GA) / np.sum(GB)
                GB = lambda_graph * GB
                print 'lambda_graph = {}'.format(lambda_graph)

                PGAT = P[k_dev].dot(GA.T)
                PGA = P[k_dev].dot(GA)
                PDA = P[k_dev].dot(DA)
                upper += GB.dot(PGAT) + GB.T.dot(PGA) + DB_SCALED.dot(PDA)

                for k_itr in xrange(K):
                    print 'The {}th component'.format(k_itr)
                    lower += P[k_itr].dot((GA.dot(P[k_itr].T)).dot(PGAT) + GA.T.dot(P[k_itr].T).dot(PGA) + DA.dot(P[k_itr].T).dot(PDA))

            P_new[k_dev] = P[k_dev] * upper / lower
            P_new[k_dev] /= np.sum(P_new[k_dev], axis=0)

            yield i, k_dev, P_new[k_dev]

        P = P_new



def main():
    for it, k, P in optimize('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/mobilitygraph_large_new/','/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/mobilitygraph_large_new/', 1000):
        print 'Iteration {}, the {}th component'.format(it, k)
        np.savetxt('./PK5B10A01/P_K{}_ITER{}.csv'.format(k, it), P, delimiter=',')

if __name__ == '__main__':
    main()
