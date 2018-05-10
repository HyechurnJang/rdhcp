# -*- coding: utf-8 -*-
'''
Created on 2018. 3. 30.
@author: HyechurnJang
'''

import os
import re
from netifaces import interfaces
from .model import Interface, NameSpace, Host

DEBUG = False

class Controller:
    
    def __init__(self):
        os.system('mkdir -p /opt/rdhcp')
        self.syncInterfaces()
    
    def checkIPFormat(self, ip):
        if re.search('^\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?$', ip): return True
        return False
    
    def checkMACFormat(self, mac):
        if re.search('^\w\w:\w\w:\w\w:\w\w:\w\w:\w\w$', mac): return True
        return False
    
    #===========================================================================
    # Interface
    #===========================================================================
    def syncInterfaces(self):
        if_list = interfaces()
        if_list.remove('lo')
        # need to remove mgmt intf
        for if_name in if_list:
            intf = Interface.one(Interface.name==if_name)
            if intf: intf.sync()
            else: Interface(if_name).create()
        for intf in Interface.list():
            if intf.name not in if_list: intf.delete()
    
    def getInterfaces(self):
        return [intf.toDict() for intf in Interface.list()]
    
    def getInterface(self, if_p):
        if if_p.isdigit(): intf = Interface.get(int(if_p))
        else: intf = Interface.one(Interface.name==if_p)
        if not intf: raise Exception('non-exist interface')
        return intf.toDict()
    
    def setInterfaceIP(self, if_p, ip, mask):
        if not self.checkIPFormat(ip): raise Exception('invalid ip string')
        if not self.checkIPFormat(mask): raise Exception('invalid mask string')
        if if_p.isdigit(): intf = Interface.get(int(if_p))
        else: intf = Interface.one(Interface.name==if_p)
        if not intf: raise Exception('non-exist interface')
        return intf.setIP(ip, mask).toDict()
    
    #===========================================================================
    # NameSpace
    #===========================================================================
    def getNameSpaces(self):
        return [ns.toDict() for ns in NameSpace.list()]
    
    def getNameSpace(self, ns_p):
        if ns_p.isdigit(): ns = NameSpace.get(int(ns_p))
        else: ns = NameSpace.one(NameSpace.name==ns_p)
        if not ns: raise Exception('non-exist namespace')
        return ns.toDict()
    
    def createNameSpace(self, name, if_p, gw='', dns='', ntp=''):
        if gw and not self.checkIPFormat(gw): raise Exception('invalid gw string')
        if dns and not self.checkIPFormat(dns): raise Exception('invalid dns string')
        if ntp and not self.checkIPFormat(ntp): raise Exception('invalid ntp string')
        if name.isdigit(): raise Exception('name must be non-digit string')
        if NameSpace.one(NameSpace.name==name): raise Exception('name is already exist')
        if if_p.isdigit(): intf = Interface.get(int(if_p))
        else: intf = Interface.one(Interface.name==if_p)
        if not intf: raise Exception('non-exist interface')
        return intf.createNameSpace(name, gw, dns, ntp).toDict()
    
    def deleteNameSpace(self, ns_p):
        if ns_p.isdigit(): ns = NameSpace.get(int(ns_p))
        else: ns = NameSpace.one(NameSpace.name==ns_p)
        if not ns: raise Exception('non-exist namespace')
        return ns.delete().toDict()
    
    #===========================================================================
    # Host
    #===========================================================================
    def getHosts(self):
        return [h.toDict() for h in Host.list()]
    
    def getHost(self, h_p):
        if h_p.isdigit(): h = Host.get(int(h_p))
        else: Host.one(Host.mac==h_p)
        if not h: raise Exception('non-exist host')
        return h.toDict()
    
    def createHost(self, ns_p, mac, ip, name=''):
        if not self.checkMACFormat(mac): raise Exception('invalid mac string')
        if not self.checkIPFormat(ip): raise Exception('invalid ip string')
        if ns_p.isdigit(): ns = NameSpace.get(int(ns_p))
        else: ns = NameSpace.one(NameSpace.name==ns_p)
        if not ns: raise Exception('non-exist namespace')
        return ns.createHost(mac, ip, name).toDict()
    
    def deleteHost(self, h_p):
        if h_p.isdigit(): h = Host.get(int(h_p))
        else: Host.one(Host.mac==h_p)
        if not h: raise Exception('non-exist host')
        return h.delete().toDict()

controller = Controller()
