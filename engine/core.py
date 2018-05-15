# -*- coding: utf-8 -*-
'''
Created on 2018. 3. 30.
@author: HyechurnJang
'''

import os
import re
from ipaddress import ip_network
from netifaces import interfaces, ifaddresses, AF_INET, AF_LINK
from .model import Interface, NameSpace, Host

DEBUG = False

class Controller:
    
    def __init__(self):
        os.system('mkdir -p /opt/rdhcp')
        self.syncInterfaces()
        self.syncNameSpace()
    
    def checkIPFormat(self, ip):
        if re.search('^\d\d?\d?\.\d\d?\d?\.\d\d?\d?\.\d\d?\d?$', ip): return True
        return False
    
    def checkMACFormat(self, mac):
        if re.search('^\w\w:\w\w:\w\w:\w\w:\w\w:\w\w$', mac): return True
        return False
    
    #===========================================================================
    # NTP
    #===========================================================================
    def syncNTP(self):
        ntp_servers = self.getNTPServers()
        server_str = ''
        for ntp_server in ntp_servers: server_str += 'server %s iburst\n' % ntp_server
        if server_str:
            with open('/etc/ntp.conf', 'w') as fd:
                fd.write('''
driftfile /var/lib/ntp/ntp.drift
statistics loopstats peerstats clockstats
filegen loopstats file loopstats type day enable
filegen peerstats file peerstats type day enable
filegen clockstats file clockstats type day enable
%s
server 127.127.1.0
fudge 127.127.1.0 stratum 10
restrict -4 default kod notrap nomodify nopeer noquery limited
restrict -6 default kod notrap nomodify nopeer noquery limited
restrict 127.0.0.1
restrict ::1
restrict source notrap nomodify noquery
                ''' % server_str)
            os.system('systemctl restart ntp')
        return ntp_servers
    
    def getNTPServers(self):
        with open('/opt/rdhcp/ntp_server_list', 'r') as fd: ntp_servers = fd.readlines()
        return filter(None, ntp_servers)
    
    def addNTPServer(self, server):
        ntp_servers = self.getNTPServers()
        for ntp_server in ntp_servers:
            if server == ntp_server: raise Exception('already exist')
        ntp_servers.append(server)
        with open('/opt/rdhcp/ntp_server_list', 'w') as fd:
            for ntp_server in ntp_servers: fd.write('%s\n' % ntp_server)
        return self.syncNTP()
    
    def delNTPServer(self, server):
        ntp_servers = self.getNTPServers()
        if server not in ntp_servers: raise Exception('non-exist server')
        ntp_servers.remove(server)
        with open('/opt/rdhcp/ntp_server_list', 'w') as fd:
            for ntp_server in ntp_servers: fd.write('%s\n' % ntp_server)
        return self.syncNTP()
    
    #===========================================================================
    # Interface
    #===========================================================================
    def syncInterfaces(self):
        if_list = interfaces()
        if_list.remove('lo')
        try:
            if_mgmt_name = os.environ.get('RDHCP_IF_MGMT', '')
            if_list.remove(if_mgmt_name)
            if_mgmt_addrs = ifaddresses(if_mgmt_name)
            if_mgmt_ip_0 = if_mgmt_addrs[AF_INET][0]
            if_mgmt_ip = if_mgmt_ip_0['addr']
            if_mgmt_mask = if_mgmt_ip_0['netmask']
            network = ip_network(unicode('%s/%s' % (if_mgmt_ip, if_mgmt_mask)), strict=False)
            if_mgmt_net = str(network.network_address)
            if_mgmt_prefix = str(network.prefixlen)
            if_mgmt_cidr = '%s/%s' % (if_mgmt_ip, if_mgmt_prefix)
            os.environ['RDHCP_IF_MGMT_IP'] = if_mgmt_ip
            os.environ['RDHCP_IF_MGMT_MASK'] = if_mgmt_mask
            os.environ['RDHCP_IF_MGMT_NET'] = if_mgmt_net
            os.environ['RDHCP_IF_MGMT_CIDR'] = if_mgmt_cidr
            os.environ['RDHCP_IF_MGMT_PREFIX'] = if_mgmt_prefix
            os.system('iptables -t nat -D POSTROUTING -o %s -j MASQUERADE' % if_mgmt_name)
            os.system('iptables -t nat -I POSTROUTING -o %s -j MASQUERADE' % if_mgmt_name)
        except Exception as e:
            print 'RDHCP_IF_MGMT is incorrect state : %s' % str(e)
            exit(1)
        try: if_list.remove('docker0')
        except: pass
        try: if_list.remove('ovs-system')
        except: pass
        for if_name in if_list:
            intf = Interface.one(Interface.name==if_name)
            if intf: intf.sync()
            elif not re.search('^rve-.+', if_name): Interface(if_name).create()
        for intf in Interface.list():
            if not intf.ns_id and intf.name not in if_list: intf.delete()
        return [intf.toDict() for intf in Interface.list()]
    
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
    def syncNameSpace(self):
        ns_list = NameSpace.list()
        for ns in ns_list: ns.sync()
        return [ns.toDict() for ns in ns_list]
    
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
        if Interface.one(Interface.name==name): raise Exception('could not set name like as interface')
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
