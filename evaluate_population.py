#!/usr/bin/env python
# encoding: utf-8

import numpy as np

n_lat = 50
n_lon = 40


def read_file(DO_rs, DO_gt, path, dis_lat, dis_lon):
    DOt = np.genfromtxt(path + 'LAT{}LON{}.csv'.format(dis_lat, dis_lon), delimiter=',')
    DO_rs[dis_lon * n_lat + dis_lat, :] = DOt[:, 0]
    DO_gt[dis_lon * n_lat + dis_lat, :] = DOt[:, 2]


def read_file_P_only(DO_wo, path, dis_lat, dis_lon):
    DOt = np.genfromtxt(path + 'LAT{}LON{}.csv'.format(dis_lat, dis_lon), delimiter=',')
    DO_wo[dis_lon * n_lat + dis_lat, :] = DOt


def read_file_noglobal(DO_hmm, path, dis_lat, dis_lon):
    DOt = np.genfromtxt(path + 'LAT{}LON{}.csv'.format(dis_lat, dis_lon), delimiter=',')
    DO_hmm[dis_lon * n_lat + dis_lat, :] = DOt


def main():
    DO_rs = np.zeros([n_lat * n_lon, 96])
    DO_gt = np.zeros([n_lat * n_lon, 96])
    DO_wo = np.zeros([n_lat * n_lon, 96])
    DO_hmm = np.zeros([n_lat * n_lon, 96])
    for dis_lat in xrange(n_lat):
        for dis_lon in xrange(n_lon):
            read_file(DO_rs, DO_gt, './density_variation/', dis_lat, dis_lon)
            read_file_P_only(DO_wo, './density_variation_P_only/', dis_lat, dis_lon)
            read_file_noglobal(DO_hmm, './density_variation_noglobal/', dis_lat, dis_lon)

    DO_rs -= np.average(DO_rs, axis=0)
    DO_gt -= np.average(DO_gt, axis=0)
    DO_wo -= np.average(DO_wo, axis=0)
    DO_hmm -= np.average(DO_hmm, axis=0)
    with open('./output_populaton_density.csv', 'w') as f:
        for t in xrange(96):
            v_rs = DO_rs[:, t]
            v_gt = DO_gt[:, t]
            v_wo = DO_wo[:, t]
            v_hmm = DO_hmm[:, t]
            r_rs = np.dot(v_rs, v_gt) / ((np.dot(v_rs, v_rs) * np.dot(v_gt, v_gt)) ** 0.5)
            r_wo = np.dot(v_wo, v_gt) / ((np.dot(v_wo, v_wo) * np.dot(v_gt, v_gt)) ** 0.5)
            r_hmm = np.dot(v_hmm, v_gt) / ((np.dot(v_hmm, v_hmm) * np.dot(v_gt, v_gt)) ** 0.5)
            f.write('{}, {}, {}\n'.format(r_rs, r_wo, r_hmm))


if __name__ == '__main__':
    main()
