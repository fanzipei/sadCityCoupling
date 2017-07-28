#!/usr/bin/env python
# encoding: utf-8

import csv
import numpy as np

trajs = dict({})

with open('./simulated_trajectories/simulated_nagoya30.csv', 'r') as f:
    for uid_str, lat_str, lon_str, time_str in csv.reader(f):
        uid = int(uid_str)
        if uid not in trajs:
            trajs[uid] = []
        trajs[uid].append((lat_str, lon_str, time_str))

with open('subset_simulated_nagoya30.csv' , 'w') as f:
    for uid in list(np.random.choice(trajs.keys(), 5000, replace=False)):
        for rec in trajs[uid]:
            f.write('{},{},{},{}\n'.format(uid, rec[0], rec[1], rec[2]))
