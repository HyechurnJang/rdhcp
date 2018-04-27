# -*- coding: utf-8 -*-
'''
Created on 2018. 4. 27.
@author: HyechurnJang
'''

import os
import json
import pygics

if __name__ == '__main__':
    
    with open('networks.json', 'r') as fd:
        networks = json.loads(fd.read())
    
    idx = 1
    for name, desc in networks.items():
        low_name = name.lower()
        os.system('brctl delif rdhcp %s0' % low_name)
        os.system('ip link del %s0' % low_name)
        os.system('ip netns del %s' % low_name)
    
    os.system('brctl delbr rdhcp')
