#!/usr/bin/env python
# encoding: utf-8

import numpy as np
from scipy import linalg as LA

def get_half_inverse(A):
    e_vals, e_vecs = LA.eigh(A)
    e_vals = e_vals ** (-0.5)
    return e_vecs.T.dot(np.diag(e_vals)).dot(e_vecs)


def main():
    P = np.random.ranf([5,4])
    print 'Iteration 0:'
    # print P
    for i in xrange(10):
        print 'Iteration {}:'.format(i+1)
        P = P.dot(get_half_inverse(P.T.dot(P)))
        # print P


if __name__ == '__main__':
    main()
