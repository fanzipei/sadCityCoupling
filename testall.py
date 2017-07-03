#!/usr/bin/env python
# encoding: utf-8

min_lat = 262
max_lat = 336 + 1
min_lon = 820
max_lon = 919 + 1


def generate_all_cases(filename):
    with open(filename,'w') as f:
        for lat in xrange(min_lat,max_lat):
            for lon in xrange(min_lon,max_lon):
                f.write('/home/fan/work/python/sadCityMapping/visualization/LAT{}LON{}.txt\n'.format(lat,lon))


def main():
    generate_all_cases('./all.txt')


if __name__ == '__main__':
    main()
