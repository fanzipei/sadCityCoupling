#!/usr/bin/env python
# encoding: utf-8

import csv

def main():
    user_set = set()
    with open('./user_list_osaka0601.csv', 'r') as f:
        for u_str, in csv.reader(f):
            u = int(u_str)
            user_set.add(u)
    with open('./gt_osaka.csv', 'r') as f:
        with open('./gt_osaka_trimmed.csv', 'w') as f_out:
            for u_str, lat_str, lon_str, time_str in csv.reader(f):
                if int(u_str) in user_set:
                    f_out.write('{},{},{},{}\n'.format(u_str, lat_str, lon_str, time_str))


if __name__ == '__main__':
    main()
