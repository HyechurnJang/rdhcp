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
        self.if_mgmt = os.environ.get('RDHCP_IF_MGMT', '')
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
        try: if_list.remove(self.if_mgmt)
        except: pass
        for if_name in if_list:
            intf = Interface.one(Interface.name==if_name)
            if intf: intf.sync()
            else: Interface(if_name).create()
        for intf in Interface.list():
            if intf.name not in if_list: intf.delete()
        return [intf.toDict() for intf in Interface.list()]
    
    def setIfMgmt(self, if_mgmt):
        self.if_mgmt = if_mgmt
        return self.syncInterfaces()
    
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
    
    def createNameSpace(self, name, if_p, stt='', end='', gw='', dns='', ntp=''):
        if stt and end:
            if not self.checkIPFormat(stt): raise Exception('invalid stt string')
            if not self.checkIPFormat(end): raise Exception('invalid end string')
            range = '%s,%s' % (stt, end)
        elif not stt and not end: range = ''
        else: raise Exception('dhcp_start and dhcp_end always must be pair value')
        if gw and not self.checkIPFormat(gw): raise Exception('invalid gw string')
        if dns and not self.checkIPFormat(dns): raise Exception('invalid dns string')
        if ntp and not self.checkIPFormat(ntp): raise Exception('invalid ntp string')
        if name.isdigit(): raise Exception('name must be non-digit string')
        if NameSpace.one(NameSpace.name==name): raise Exception('name is already exist')
        if if_p.isdigit(): intf = Interface.get(int(if_p))
        else: intf = Interface.one(Interface.name==if_p)
        if not intf: raise Exception('non-exist interface')
        return intf.createNameSpace(name, range, gw, dns, ntp).toDict()
    
    def deleteNameSpace(self, ns_p):
        if ns_p.isdigit(): ns = NameSpace.get(int(ns_p))
        else: ns = NameSpace.one(NameSpace.name==ns_p)
        if not ns: raise Exception('non-exist namespace')
        return ns.delete().toDict()
    
    #===========================================================================
    # Host
    #===========================================================================
    def getHosts(self, ns_p=None):
        if ns_p:
            if ns_p.isdigit(): ns = NameSpace.get(int(ns_p))
            else: ns = NameSpace.one(NameSpace.name==ns_p)
            if not ns: raise Exception('non-exist namespace')
            return [h.toDict() for h in Host.list(Host.ns_id==ns.id)]
        return [h.toDict() for h in Host.list()]
    
    def getHost(self, h_p):
        if h_p.isdigit(): h = Host.get(int(h_p))
        else: h = Host.one(Host.mac==h_p)
        if not h: raise Exception('non-exist host')
        return h.toDict()
    
    def findHost(self, ns_p, ip):
        if ns_p.isdigit(): ns = NameSpace.get(int(ns_p))
        else: ns = NameSpace.one(NameSpace.name==ns_p)
        if not ns: raise Exception('non-exist namespace')
        h = Host.one(Host.ns_id==ns.id, Host.ip==ip)
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
        else: h = Host.one(Host.mac==h_p)
        if not h: raise Exception('non-exist host')
        return h.delete().toDict()

controller = Controller()
