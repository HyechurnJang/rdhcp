# -*- coding: utf-8 -*-
'''
Created on 2018. 3. 30.
@author: HyechurnJang
'''

import os
import re
import json
from ipaddress import ip_network
from netifaces import interfaces, ifaddresses, AF_INET, AF_LINK
from .model import Interface, NameSpace, Host

DEBUG = False

class Controller:
    
    def __init__(self, mgmt_if_name=None):
        self.mgmt_if_name = mgmt_if_name
        self.if_list = []
        self.if_used = []
        self.ns_list = []
        self.syncInterface()
    
    def cli(self, cmd, force=False):
        if DEBUG: print cmd
        else:
            ret = os.system(cmd)
            if ret > 0 and not force: raise Exception('CMD(%s) >> %d' % (cmd, ret))
    
    def syncInterface(self):
        self.if_list = interfaces()
        self.if_list.remove('lo')
        for if_name in self.if_list:
            addrs = ifaddresses(if_name)
            try: mac = addrs[AF_LINK][0]['addr']
            except: mac = '00:00:00:00:00:00'
            try:
                ip_0 = addrs[AF_INET][0]
                ip = ip_0['addr']
                mask = ip_0['netmask']
            except:
                ip = '0.0.0.0'
                mask = '255.255.255.255'
            try:
                net_o = ip_network('%s/%s' % (ip, mask), strict=False)
                net = str(net_o.network_address)
                prefix = str(net_o.prefixlen)
            except:
                net = '255.255.255.255'
                prefix = '32'
            cidr = '%s/%s' % (ip, prefix)
            intf = Interface.one(Interface.name==if_name)
            if intf:
                if not intf.ns:
                    intf.mac = mac
                    intf.ip = ip
                    intf.net = net
                    intf.mask = mask
                    intf.cidr = cidr
                    intf.prefix = prefix
                    intf.update()
            else:
                Interface(if_name, mac, ip, net, mask, cidr, prefix).create()
        intfs = Interface.list()
        for intf in intfs:
            if intf.name not in self.if_list: intf.delete()
    
    def setInterface(self, if_name, ip, mask):
        if if_name not in self.if_list: return None
        if not re.search('^\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?$', ip): return None
        if not re.search('^\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?$', mask): return None
        
        intf = Interface.one(Interface.name==if_name)
        if intf.ns: return None
        
        try: self.cli('ifconfig %s %s netmask %s up' % (if_name, ip, mask))
        except Exception as e: raise e
        
        intf.ip = ip
        intf.mask = mask
        net_obj = ip_network(unicode('%s/%s' % (ip, mask)), strict=False)
        intf.net = net_obj.network_address
        intf.prefix = net_obj.prefixlen
        intf.cidr = '%s/%s' % (ip, intf.prefix)
        intf.update()
        return intf
    
    def createNamespace(self, name, if_name, gw='', dhcp='', dns='', ntp=''):
        if name in self.ns_list: return None
        if if_name not in self.if_list: return None
        if if_name in self.if_used: return None
        
        intf = Interface.one(Interface.name==if_name)
        mac = intf.mac
        nac = 'aa:aa:aa' + mac[9:]
        cidr = intf.cidr
        
        try:
            self.cli('ip netns add %s' % name)
            self.cli('brctl addbr %s' % name)
            self.cli('ifconfig %s up' % name)
            self.cli('ip link add v%s type veth peer name v%s netns %s' % (name, name, name))
            self.cli('ifconfig v%s 0.0.0.0 up' % name)
            self.cli('ip netns exec %s ifconfig lo up' % name)
            self.cli('ifconfig %s 0.0.0.0 up' % if_name)
            self.cli('ifconfig %s hw ether %s' % (if_name, nac))
            self.cli('ip netns exec %s ifconfig v%s %s up' % (name, name, cidr))
            self.cli('ip netns exec %s ifconfig v%s hw ether %s' % (name, name, mac))
            self.cli('brctl addif %s v%s' % (name, name))
            self.cli('brctl addif %s %s' % (name, if_name))
        except Exception as e:
            self.deleteNamespace(name, if_name)
            raise e
        
        self.if_used.append(if_name)
        self.ns_list.append(name)
        return NameSpace(name, if_name, intf.net, intf.mask, gw, dhcp, dns, ntp).create()
        
    def deleteNamespace(self, name, if_name):
        if name not in self.ns_list: return None
        if if_name not in self.if_list: return None
        if if_name not in self.if_used: return None
        
        intf = Interface.one(Interface.name==if_name)
        mac = intf.mac
        cidr = intf.cidr
        
        try:
            self.cli('ip netns del %s' % name, force=True)
            self.cli('ifconfig %s down' % name, force=True)
            self.cli('brctl delbr %s' % name, force=True)
            self.cli('ifconfig %s %s up' % (if_name, cidr), force=True)
            self.cli('ifconfig %s hw ether %s' % (if_name, mac), force=True)
        except Exception as e:
            raise e
        
        self.if_used.remove(if_name)
        self.ns_list.remove(name)
        ns_o = NameSpace.one(NameSpace.name==name)
        return ns_o.delete()

controller = Controller()
