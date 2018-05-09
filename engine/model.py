# -*- coding: utf-8 -*-
'''
Created on 2018. 3. 30.
@author: HyechurnJang
'''

from sql import *

# db = Sql(File())
db = Sql(Mysql('localhost', 'root', '1234Qwer', 'rdhcp'))

@model(db)
class Interface(Model):
    
    name = String(32)
    mac = String(24)
    ip = String(16)
    net = String(16)
    mask = String(16)
    cidr = String(24)
    prefix = String(4)
    ns = String(32)
    
    def __init__(self, name, mac, ip, net, mask, cidr, prefix):
        self.name = name
        self.mac = mac 
        self.ip = ip
        self.net = net
        self.mask = mask
        self.cidr = cidr
        self.prefix = prefix
        self.ns = ''
    
    def __repr__(self):
        return 'Interface(%s, %s, %s, %s, %s, %s, %s, %s)' % (
            self.name,
            self.mac,
            self.ip,
            self.net,
            self.mask,
            self.cidr,
            self.prefix,
            self.ns
        )
    
    def toDict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'mac' : self.mac,
            'ip' : self.ip,
            'net' : self.net,
            'mask' : self.mask,
            'cidr' : self.cidr,
            'prefix' : self.prefix,
            'ns' : self.ns
        }

@model(db)
class NameSpace(Model):
    
    name = String(32)
    intf = String(32)
    net = String(16)
    mask = String(16)
    prefix = String(4)
    gateway = String(16)
    dhcp = String(16)
    dns = String(16)
    ntp = String(16)
    
    def __init__(self, name, intf, net, mask, gw, dhcp, dns, ntp):
        self.name = name
        self.intf = intf
        self.net = net
        self.mask = mask
        self.gw = gw
        self.dhcp = dhcp
        self.dns = dns
        self.ntp = ntp
    
    def __repr__(self):
        return 'Net(%s, %s, %s, %s, %s, %s, %s, %s)' % (
            self.name,
            self.intf,
            self.net,
            self.mask,
            self.gw,
            self.dhcp,
            self.dns,
            self.ntp
        )
    
    def toDict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'intf' : self.intf,
            'net' : self.net,
            'mask' : self.mask,
            'gw' : self.gw,
            'dhcp' : self.dhcp,
            'dns' : self.dns,
            'ntp' : self.ntp
        }

@model(db)
class Host(Model):
    
    ns = String(32)
    mac = String(24)
    ip = String(16)
    
    def __init__(self, ns, mac, ip):
        self.ns = ns
        self.mac = mac
        self.ip = ip
    
    def __repr__(self):
        return 'Host(%s, %s, %s)' % (self.ns, self.mac, self.ip)
    
    def toDict(self):
        return {
            'id' : self.id,
            'ns' : self.ns,
            'mac' : self.mac,
            'ip' : self.ip
        }
