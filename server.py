# -*- coding: utf-8 -*-
'''
Created on 2018. 4. 27.
@author: HyechurnJang
'''

import os
import pygics
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mgmt', help='Restricted Mgmt NIC for NameSpace', default='')
    args = parser.parse_args()
    os.environ['RDHCP_MGMT_NIC'] = args.mgmt
    pygics.server('0.0.0.0', 8080, 'engine')