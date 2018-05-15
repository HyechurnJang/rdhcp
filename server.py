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
    
    parser.add_argument('-m', '--mgmt', help='Restricted Mgmt NIC for NameSpace', required=True)
    parser.add_argument('-d', '--database', help='MySQL Database Hostname or IP', default='localhost')
    parser.add_argument('-p', '--password', help='MySQL Root Password', default='rdhcp')
    args = parser.parse_args()
    os.environ['RDHCP_IF_MGMT'] = args.mgmt
    os.environ['RDHCP_DATABASE'] = args.database
    os.environ['RDHCP_PASSWORD'] = args.password
    
    pygics.server('0.0.0.0', 8080, 'engine')