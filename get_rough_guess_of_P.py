#!/usr/bin/env python
# encoding: utf-8

import numpy as np
from numpy.linalg import inv

miu = 0.010

def main():
    XO = np.genfromtxt('/media/fan/HDPC-UT/ZDC/TrainingForMapping/node_fukuoka.csv', delimiter=',', dtype=np.float)
    XT = np.genfromtxt('/media/fan/HDPC-UT/ZDC/TrainingForMapping/node_nagoya.csv', delimiter=',', dtype=np.float)
    XO /= np.sum(XO, axis=0)
    XT /= np.sum(XT, axis=0)
    P = np.random.ranf([XO.shape[0], XT.shape[0]]) * 0.0010
    for i in xrange(30):
        print i
        P *= (XO.dot(XT.T) + miu) / (P.dot(XT.dot(XT.T)) + miu * np.sum(P, axis=0) )
        P /= np.sum(P, axis=0)
    np.savetxt('P_nagoya2fukuoka.csv', P, delimiter=',')


if __name__ == '__main__':
    main()
