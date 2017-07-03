#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import csv

graph_dict = dict({})
node_density = dict({})

def read_file(filename,t):
    with open(filename,'r') as f:
        for loc_ori_str,loc_des_str,cnt_str in csv.reader(f):
            loc_ori = int(loc_ori_str)
            loc_des = int(loc_des_str)
            cnt = int(cnt_str)
            if loc_ori == loc_des:
                if loc_ori not in node_density:
                    node_density[loc_ori] = np.zeros(2880,np.int32)
                node_density[loc_ori][t] = cnt
            else:
                if (loc_ori,loc_des) not in graph_dict:
                    graph_dict[(loc_ori,loc_des)] = np.zeros(48,np.int32)
                    graph_dict[(loc_ori,loc_des)][t%48] = cnt
                else:
                    graph_dict[(loc_ori,loc_des)][t%48] += cnt


def output_edge_file(filename,t):
    with open(filename,'w') as f:
        for (loc_ori,loc_des) in graph_dict:
            if graph_dict[(loc_ori,loc_des)][t] > 0:
                f.write('{},{},{}\n'.format(loc_ori,loc_des,graph_dict[(loc_ori,loc_des)][t]))


def output_node_file(filename):
    with open(filename,'w') as f:
        for loc_idx in node_density:
            for t in xrange(2879):
                f.write('{},'.format(node_density[loc_idx][t]))
            f.write('{}\n'.format(node_density[loc_idx][-1]))


def main():
    for t in xrange(2880):
        read_file('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/mobilitygraph_large_new/graph_H{}_30.csv'.format(t),t)
    # output
    for t in xrange(48):
        output_edge_file('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/aggregated_mobilitygraph_large/agraph_H{}_30.csv'.format(t),t)
    output_node_file('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/aggregated_mobilitygraph_large/node.csv')

if __name__ == '__main__':
    main()
