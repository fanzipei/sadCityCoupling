#!/usr/bin/env python
# encoding: utf-8

import csv
import time
import bisect
import numpy as np

# Tokyo
lat_min = 35.5
lat_max = 35.796
lon_min = 139.4
lon_max = 139.9
# Osaka
#  lat_min = 34.45
#  lat_max = 34.85
#  lon_min = 135.3
#  lon_max = 135.7
num_dislat = int( ( lat_max - lat_min + 0.00001 )/0.008 )
num_dislon = int( ( lon_max - lon_min + 0.00001 )/0.010 )

traj_set = dict({})

def get_loc_idx(lat,lon):
    if lat > lat_max or lon > lon_max:
        return -1
    dis_lat = int( (min(lat, lat_max - 0.00001) - lat_min) / 0.008 )
    dis_lon = int( (min(lon, lon_max - 0.00001) - lon_min) / 0.010 )
    return dis_lat + dis_lon*num_dislat

class SingleTraj:
    def __init__(self,cur_time,rec):
        self._traj = [rec]
        self.update_start_time(cur_time)

    def update_start_time(self,cur_time):
        del self._traj[:bisect.bisect([a[0] for a in self._traj],cur_time-3600*24)]

    def isEmpty(self):
        return len(self._traj) < 1

    def insert_record(self,rec):
        self._traj.append(rec)

    def get_by_time(self,tstamp):
        pre_rec = self._traj[0]
        if pre_rec[0] > tstamp:
            return pre_rec[1],pre_rec[2]

        for rec in self._traj:
            if rec[0] > tstamp:
                dt = rec[0] - pre_rec[0]
                dlat = rec[1] - pre_rec[1]
                dlon = rec[2] - pre_rec[2]
                ratio = ( tstamp - pre_rec[0] ) / dt
                lat = pre_rec[1] + ratio * dlat
                lon = pre_rec[2] + ratio * dlon
                return lat,lon
            else:
                pre_rec = rec

        return pre_rec[1],pre_rec[2]

def load_file(filename,cur_time):
    print 'Load file:' + filename
    for u in traj_set:
        traj_set[u].update_start_time(cur_time)

    with open(filename,'r') as f:
        for u_str,time_str,lat_str,lon_str in csv.reader(f):
            u = int(u_str)
            tstamp = time.mktime(time.strptime(time_str,'%Y-%m-%d %H:%M:%S'))
            lat = float(lat_str)
            lon = float(lon_str)

            if u in traj_set:
                traj_set[u].insert_record((tstamp,lat,lon))
            else:
                traj_set[u] = SingleTraj(cur_time,(tstamp,lat,lon))

def build_graph(in_dirpath,out_dirpath):
    start_time = time.mktime(time.strptime('2012-06-01 00:00:00','%Y-%m-%d %H:%M:%S')) + 3600 * 12
    end_time = time.mktime(time.strptime('2012-08-01 00:00:00','%Y-%m-%d %H:%M:%S')) - 3600 * 12 - 1

    full_path = in_dirpath + time.strftime('%Y%m%d',time.localtime(start_time)) + '.csv'
    load_file(full_path,start_time)

    for t in xrange(int(start_time),int(end_time),1800):

        # graph_30 = np.zeros([num_dislat*num_dislon,num_dislat*num_dislon],np.int32)
        # graph_20 = np.zeros([num_dislat*num_dislon,num_dislat*num_dislon],np.int32)
        # graph_10 = np.zeros([num_dislat*num_dislon,num_dislat*num_dislon],np.int32)
        graph_30 = dict({})
        # graph_20 = dict({})
        # graph_10 = dict({})

        hours_passed = int( t - start_time ) / 1800
        if hours_passed % 48 == 0:
            nextday_tstamp = t + 3600 * 24
            full_path = in_dirpath + time.strftime('%Y%m%d',time.localtime(nextday_tstamp)) + '.csv'
            load_file(full_path,t)
            empty_users = [u for u in traj_set if traj_set[u].isEmpty()]
            for u in empty_users:
                del traj_set[u]

        for u in traj_set:
            if traj_set[u].isEmpty():
                continue
            lat_pre_30,lon_pre_30 = traj_set[u].get_by_time(t-1800)
            idx_pre_30 = get_loc_idx(lat_pre_30,lon_pre_30)
            # lat_pre_20,lon_pre_20 = traj_set[u].get_by_time(t-1200)
            # idx_pre_20 = get_loc_idx(lat_pre_20,lon_pre_20)
            # lat_pre_10,lon_pre_10 = traj_set[u].get_by_time(t-600)
            # idx_pre_10 = get_loc_idx(lat_pre_10,lon_pre_10)
            # lat_pro_10,lon_pro_10 = traj_set[u].get_by_time(t+600)
            # idx_pro_10 = get_loc_idx(lat_pro_10,lon_pro_10)
            # lat_pro_20,lon_pro_20 = traj_set[u].get_by_time(t+1200)
            # idx_pro_20 = get_loc_idx(lat_pro_20,lon_pro_20)
            lat_pro_30,lon_pro_30 = traj_set[u].get_by_time(t+1800)
            idx_pro_30 = get_loc_idx(lat_pro_30,lon_pro_30)
            if idx_pre_30 < 0 or idx_pro_30 < 0:
                continue
            if (idx_pre_30,idx_pro_30) in graph_30:
                graph_30[(idx_pre_30,idx_pro_30)] += 1
            else:
                graph_30[(idx_pre_30,idx_pro_30)] = 1

            # if (idx_pre_20,idx_pro_20) in graph_20:
                # graph_20[(idx_pre_20,idx_pro_20)] += 1
            # else:
                # graph_20[(idx_pre_20,idx_pro_20)] = 1

            # if (idx_pre_10,idx_pro_10) in graph_10:
                # graph_10[(idx_pre_10,idx_pro_10)] += 1
            # else:
                # graph_10[(idx_pre_10,idx_pro_10)] = 1
            # graph_30[(idx_pre_30,idx_pro_30)] += 1
            # graph_20[(idx_pre_20,idx_pro_20)] += 1
            # graph_10[(idx_pre_10,idx_pro_10)] += 1

        out_filename = out_dirpath + 'graph_H{}_30.csv'.format(hours_passed)
        with open(out_filename,'w') as f:
            for (idx_pre,idx_pro) in graph_30:
                f.write('{},{},{}\n'.format(idx_pre,idx_pro,graph_30[(idx_pre,idx_pro)]))
        print 'Save ' + out_filename
        # out_filename = out_dirpath + 'graph_H{}_20.csv'.format(hours_passed)
        # with open(out_filename,'w') as f:
            # for (idx_pre,idx_pro) in graph_20:
                # f.write('{},{},{}\n'.format(idx_pre,idx_pro,graph_20[(idx_pre,idx_pro)]))
        # print 'Save ' + out_filename
        # out_filename = out_dirpath + 'graph_H{}_10.csv'.format(hours_passed)
        # with open(out_filename,'w') as f:
            # for (idx_pre,idx_pro) in graph_10:
                # f.write('{},{},{}\n'.format(idx_pre,idx_pro,graph_10[(idx_pre,idx_pro)]))
        # print 'Save ' + out_filename
        # out_filename = out_dirpath + 'graph_H{}_30.csv'.format(hours_passed)
        # np.savetxt(out_filename,graph_30,delimiter=',',fmt='%u')
        # print 'Save ' + out_filename
        # out_filename = out_dirpath + 'graph_H{}_20.csv'.format(hours_passed)
        # np.savetxt(out_filename,graph_20,delimiter=',',fmt='%u')
        # print 'Save ' + out_filename
        # out_filename = out_dirpath + 'graph_H{}_10.csv'.format(hours_passed)
        # np.savetxt(out_filename,graph_10,delimiter=',',fmt='%u')
        # print 'Save ' + out_filename

def main():
    print num_dislat
    print num_dislon
    build_graph('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/sorted/','/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/mobilitygraph_large_new/')
    #  build_graph('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/sorted/','/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/mobilitygraph_large_new/')

if __name__ == '__main__':
    main()
