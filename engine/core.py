# -*- coding: utf-8 -*-
'''
Created on 2018. 3. 30.
@author: HyechurnJang
'''

import os
import json
import subprocess
from pygics import Lock

class Controller:
    
    def __init__(self):
        with open('networks.json', 'r') as fd:
            self.networks = json.loads(fd.read())
        
        print('brctl addbr rdhcp')
        print('ifconfig rdhcp 1.254.1.254 netmask 255.255.255.0 up')
        
        for name, desc in self.networks.items():
            low_name = name.lower()
            print('ip netns add %s' % low_name)
            print('ip link add %s0 type veth peer name %s0 netns %s' % (low_name, low_name, low_name))
            print('')
            print('')
            print('')
            print('')
            print('')
            print('')
            print('')
            
        


controller = Controller()