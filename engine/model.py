# -*- coding: utf-8 -*-
'''
Created on 2018. 3. 30.
@author: HyechurnJang
'''

from sql import *

db = Sql(File())

@model(db)
class Net(Model):
    
    intf = String(32)
    network = String(16)
    netmask = String(16)
    gateway = String(16)
    dhcp = String(16)
    dns = String(16)
    ntp = String(16)
    
    def __init__(self, intf, network, netmask, gateway, dhcp, dns, ntp):
        self.intf = intf
        self.network = network
        self.netmask = netmask
        self.gateway = gateway
        self.dhcp = dhcp
        self.dns = dns
        self.ntp = ntp
    
    def __repr__(self):
        return 'Net(%s, %s, %s, %s, %s, %s, %s)' % (
            self.intf,
            self.network,
            self.netmask,
            self.gateway,
            self.dhcp,
            self.dns,
            self.ntp
        )
    
    def toDict(self):
        return {
            'id' : self.id,
            'intf' : self.intf,
            'network' : self.network,
            'netmask' : self.netmask,
            'gateway' : self.gateway,
            'dhcp' : self.dhcp,
            'dns' : self.dns,
            'ntp' : self.ntp
        }

@model(db)
class Host(Model):
    
    net_id = Integer()
    intf = String(32)
    mac = String(24)
    ip = String(16)
    
    def __init__(self, net_id, mac, ip):
        self.net_id = net_id
        self.mac = mac
        self.ip = ip
    
    def __repr__(self):
        return 'Host(%s, %s, %s)' % (self.intf, self.mac, self.ip)
    
    def toDict(self):
        return {
            'id' : self.id,
            'net_id' : self.net_id,
            'intf' : self.intf,
            'mac' : self.mac,
            'ip' : self.ip
        }
