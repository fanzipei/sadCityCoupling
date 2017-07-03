#!/usr/bin/env python
# encoding: utf-8

import csv
import numpy as np

# Tokyo
lat_min_t = 35.5
lat_max_t = 35.796
lon_min_t = 139.4
lon_max_t = 139.9
num_loc_t = 1850
num_dislat_t = 37
# Osaka
lat_min_o = 34.45
lat_max_o = 34.85
lon_min_o = 135.3
lon_max_o = 135.7
num_loc_o = 2000
num_dislat_o = 50

def output_visualization(W,dir_path):
    for i in xrange(W.shape[0]):
        v = W[i,:]
        v /= max(v)
        # v = v ** 0.25
        dis_lat_t = i%num_dislat_t
        dis_lon_t = i/num_dislat_t
        with open(dir_path+'LAT{}LON{}.txt'.format(dis_lat_t,dis_lon_t),'w') as f:
            for j in xrange(W.shape[1]):
                dis_lat_o,dis_lon_o = j%num_dislat_o, j/num_dislat_o
                f.write('{}\t{}\t{}\t{}\t{}\n'.format(dis_lat_o,dis_lon_o,v[j],0.5,1-v[j]))


def main():
    tokyo_ring = [(22, 36), (19, 39), (23, 30), (16, 33), (20, 35), (24, 37), (26, 37), (28, 31), (29, 36)]
    W = np.genfromtxt('./dp_rst/P_ITER199.csv', delimiter=',').T
    print W.shape
    print 'Read Transition Matrix Complete'
    osaka_vec = np.zeros(num_loc_o)
    for dis_lat, dis_lon in tokyo_ring:
        tokyo_idx = dis_lon * num_dislat_t + dis_lat
        osaka_vec += W[tokyo_idx, :]
    osaka_vec /= max(osaka_vec)
    with open('osaka_ring.txt', 'w') as f:
        for j in xrange(num_loc_o):
            dis_lat_o,dis_lon_o = j%num_dislat_o, j/num_dislat_o
            f.write('{}\t{}\t{}\t{}\t{}\n'.format(dis_lat_o,dis_lon_o,osaka_vec[j],0.5,1-osaka_vec[j]))
    output_visualization(W,'./visualization/')


if __name__ == '__main__':
    main()
