#!/usr/bin/env python
# encoding: utf-8

import csv
import time

def main():
    for t in xrange(6,4*144):
        with open('./gt_c80/output{}.csv'.format(t),'w') as f_out:
            for i in xrange(6):
                with open('/home/fan/work/data/CityMomentum/10min_c80/D{}T{}.csv'.format((t+i+1)/144,(t+i+1)%144),'r') as f_data:
                    for u_str,time_str,lat_str,lon_str in csv.reader(f_data):
                        f_out.write('{},{},{},{}\n'.format(u_str,lat_str,lon_str,time_str))

if __name__ == '__main__':
    main()
