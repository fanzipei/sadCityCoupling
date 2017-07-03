#!/usr/bin/env python
# encoding: utf-8

import colorsys
import numpy as np
import math

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

def get_distance_matrix(num_loc, num_lat):
    distance_matrix = np.zeros([num_loc, num_loc], np.float)
    for i in xrange(num_loc):
        for j in xrange(num_loc):
            dis_lat_i = i % num_lat
            dis_lon_i = i / num_lat
            dis_lat_j = j % num_lat
            dis_lon_j = j / num_lat
            distance_matrix[(i, j)] = (((dis_lat_i - dis_lat_j) ** 2 + (dis_lon_i - dis_lon_j) ** 2) ** 0.5) + 0.4

    return distance_matrix


def output_visualization(log_distance_matrix_o_array, i):
    value_matrix = np.exp(log_distance_matrix_o_array[i])
    min_val = np.min(value_matrix)
    max_val = np.max(value_matrix)
    value_matrix = (value_matrix - min_val) / (max_val - min_val)
    with open('/home/fan/workspace/sadJMapViewer/location{}.txt'.format(i), 'w') as f:
        lidx_o = 1030
        for i in xrange(num_loc_o):
            dis_lat_i = i % num_lat_o
            dis_lon_i = i / num_lat_o
            value = value_matrix[(lidx_o, i)]
            #  r, g, b = colorsys.hsv_to_rgb(value * 0.9 + 0.1, 1.0, 1.0)
            f.write('{}\t{}\t{}\t{}\t{}\n'.format(dis_lat_i, dis_lon_i, value, 0.0, 1-value))


def main():
    distance_matrix_o = get_distance_matrix(num_loc_o, num_lat_o)
    distance_matrix_t = get_distance_matrix(num_loc_t, num_lat_t)
    distance_matrix_t = np.round(distance_matrix_t).astype(int)
    log_distance_matrix_o_array = [ -math.lgamma(i + 0.4) + (i-0.6) * np.log(distance_matrix_o) - distance_matrix_o for i in xrange(np.max(distance_matrix_t)+1)]
    output_visualization(log_distance_matrix_o_array, 0)
    output_visualization(log_distance_matrix_o_array, 1)
    output_visualization(log_distance_matrix_o_array, 5)
    output_visualization(log_distance_matrix_o_array, 10)

if __name__ == '__main__':
    main()
