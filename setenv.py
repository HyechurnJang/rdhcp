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
    
    os.system('brctl addbr rdhcp')
    os.system('ifconfig rdhcp 1.254.1.254 netmask 255.255.255.0 up')
    
    idx = 1
    for name, desc in networks.items():
        low_name = name.lower()
        os.system('ip netns add %s' % low_name)
        os.system('ip link add %s0 type veth peer name %s0 netns %s' % (low_name, low_name, low_name))
        os.system('ifconfig %s0 up' % low_name)
        os.system('ip netns exec %s ifconfig %s0 1.254.1.%d netmask 255.255.255.0 up' % (low_name, low_name, idx))
        os.system('ip netns exec %s ifconfig lo up' % low_name)
        os.system('brctl addif rdhcp %s0' % low_name)
        os.system('ip link set %s netns %s' % (desc['interface'], low_name))
        os.system('ip netns exec %s ifconfig %s %s netmask %s up' % (low_name, desc['interface'], desc['address'], desc['netmask']))
        os.system('ip netns exec %s route add default gw %s' % (low_name, desc['gateway']))
        os.system('ip netns exec %s iptables -t nat -A POSTROUTING -j MASQUERADE' % low_name)
        os.system('ip netns exec %s iptables -t nat -A PREROUTING -p tcp -i %s --dport 8080 -j DNAT --to 1.254.1.254:8080' % (low_name, desc['interface']))
        os.system('ip netns exec %s iptables -t nat -A PREROUTING -p tcp -i %s --dport 22 -j DNAT --to 1.254.1.254:22' % (low_name, desc['interface']))
        idx += 1
