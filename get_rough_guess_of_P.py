#!/usr/bin/env python
# encoding: utf-8

import numpy as np
from numpy.linalg import inv

miu = 0.010

def main():
    XO = np.genfromtxt('/media/fan/HDPC-UT/ZDC/TrainingForMapping/osaka/aggregated_mobilitygraph_large/node.csv', delimiter=',', dtype=np.float)
    XT = np.genfromtxt('/media/fan/HDPC-UT/ZDC/TrainingForMapping/tokyo/aggregated_mobilitygraph_large/node.csv', delimiter=',', dtype=np.float)
    XO /= np.sum(XO, axis=0)
    XT /= np.sum(XT, axis=0)
    P = np.random.ranf([2000, 1850]) * 0.0010
    for i in xrange(30):
        print i
        P *= (XO.dot(XT.T) + miu) / (P.dot(XT.dot(XT.T)) + miu * np.sum(P, axis=0) )
        #  P = (P.T / np.sum(P.T, axis=0)).T
    np.savetxt('XO_NORMALIZED.csv', XO, delimiter=',')
    np.savetxt('XO_ESTIMATED.csv', P.dot(XT), delimiter=',')
    np.savetxt('P.csv', P, delimiter=',')


if __name__ == '__main__':
    main()
