# -*- coding: utf-8 -*-
'''
Created on 2018. 3. 30.
@author: HyechurnJang
'''

import os
from sql import *
from ipaddress import ip_network
from netifaces import interfaces, ifaddresses, AF_INET, AF_LINK

DEBUG = True

# db = Sql(File())
db = Sql(Mysql('localhost', 'root', '1234Qwer', 'rdhcp'))

def cli(cmd, force=False):
    ret = os.system(cmd)
    if ret > 0 and not force: raise Exception('CMD(%s) >> %d' % (cmd, ret))

@model(db)
class Interface(Model):
    
    name = String(32)
    ns_id = Integer()
    ns_name = String(32)
    mac = String(24)
    ip = String(16)
    net = String(16)
    mask = String(16)
    cidr = String(24)
    prefix = String(4)
    
    def __init__(self, name):
        self.name = name
        self.ns_id = 0
        self.ns_name = ''
        self.__sync__()
        
    def __sync__(self):
        addrs = ifaddresses(self.name)
        try: self.mac = addrs[AF_LINK][0]['addr']
        except: self.mac = '00:00:00:00:00:00'
        try:
            ip_0 = addrs[AF_INET][0]
            self.ip = ip_0['addr']
            self.mask = ip_0['netmask']
        except:
            self.ip = '0.0.0.0'
            self.mask = '255.255.255.255'
        try:
            network = ip_network(unicode('%s/%s' % (self.ip, self.mask)), strict=False)
            self.net = str(network.network_address)
            self.prefix = str(network.prefixlen)
        except:
            self.net = '255.255.255.255'
            self.prefix = '32'
        self.cidr = '%s/%s' % (self.ip, self.prefix)
    
    def sync(self):
        if not self.ns_id:
            self.__sync__()
            self.update()
        return self
    
    def setIP(self, ip, mask):
        if self.ns_id: raise Exception('interface assigned to namespace')
        cli('ifconfig %s %s netmask %s up' % (self.name, ip, mask))
        self.ip = ip
        self.mask = mask
        try:
            network = ip_network(unicode('%s/%s' % (self.ip, self.mask)), strict=False)
            self.net = str(network.network_address)
            self.prefix = str(network.prefixlen)
        except:
            self.net = '255.255.255.255'
            self.prefix = '32'
        self.cidr = '%s/%s' % (self.ip, self.prefix)
        self.update()
        return self
    
    def createNameSpace(self, ns_name, gw='', dns='', ntp=''):
        if self.ns_id: raise Exception('interface assigned to namespace')
        ns = NameSpace(self, ns_name, gw, dns, ntp).create()
        self.ns_id = ns.id
        self.ns_name = ns.name
        self.update()
        return ns
    
    def toDict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'ns_id' : self.ns_id,
            'ns_name' : self.ns_name,
            'mac' : self.mac,
            'ip' : self.ip,
            'net' : self.net,
            'mask' : self.mask,
            'cidr' : self.cidr,
            'prefix' : self.prefix
        }

@model(db)
class NameSpace(Model):
    
    name = String(32)
    pid = Integer()
    if_id = Integer()
    if_name = String(32)
    if_mac = String(24)
    if_ip = String(16)
    net = String(16)
    mask = String(16)
    gw = String(16)
    dns = String(16)
    ntp = String(16)
    
    def __init__(self, intf, name, gw, dns, ntp):
        self.name = name
        self.pid = 0
        self.if_id = intf.id
        self.if_name = intf.name
        self.if_mac = intf.mac
        self.if_ip = intf.ip
        self.net = intf.net
        self.mask = intf.mask
        self.gw = gw
        self.dns = dns
        self.ntp = ntp
    
    def create(self):
        dummy_mac = 'aa:aa:aa' + self.if_mac[9:]
        try:
            cli('ip netns add %s' % self.name)
            cli('brctl addbr %s' % self.name)
            cli('ifconfig %s up' % self.name)
            cli('ip link add v%s type veth peer name v%s netns %s' % (self.name, self.name, self.name))
            cli('ifconfig v%s 0.0.0.0 up' % self.name)
            cli('ip netns exec %s ifconfig lo up' % self.name)
            cli('ifconfig %s 0.0.0.0 up' % self.if_name)
            cli('ifconfig %s hw ether %s' % (self.if_name, dummy_mac))
            cli('ip netns exec %s ifconfig v%s %s netmask %s up' % (self.name, self.name, self.if_ip, self.mask))
            cli('ip netns exec %s ifconfig v%s hw ether %s' % (self.name, self.name, self.if_mac))
            cli('brctl addif %s v%s' % (self.name, self.name))
            cli('brctl addif %s %s' % (self.name, self.if_name))
            cli('mkdir -p /opt/rdhcp/%s' % self.name)
            with open('/opt/rdhcp/%s/dhcp' % self.name, 'w') as fd:
                fd.write('dhcp-option=1,%s\ndhcp-range=%s,%s\n' % (self.mask, self.net, self.net))
            cli('touch /opt/rdhcp/%s/hosts' % self.name)
            cli('ip netns exec %s /usr/sbin/dnsmasq --no-resolv --no-poll --no-hosts --interface=v%s --log-facility=/opt/rdhcp/%s/log --dhcp-leasefile=/opt/rdhcp/%s/lease --pid-file=/opt/rdhcp/%s/pid --conf-file=/opt/rdhcp/%s/dhcp --addn-hosts=/opt/rdhcp/%s/hosts' % (self.name, self.name, self.name, self.name, self.name, self.name, self.name))
            with open('/opt/rdhcp/%s/pid' % self.name, 'r') as fd:
                self.pid = int(fd.read())
        except Exception as e:
            self.__delete_namespace__()
            raise e
        return Model.create(self)
    
    def __delete_namespace__(self):
        cli('ip netns exec %s kill -9 %d' % (self.name, self.pid), force=True)
        cli('ip netns del %s' % self.name, force=True)
        cli('ifconfig %s down' % self.name, force=True)
        cli('brctl delbr %s' % self.name, force=True)
        cli('ifconfig %s %s netmask %s up' % (self.if_name, self.if_ip, self.mask), force=True)
        cli('ifconfig %s hw ether %s' % (self.if_name, self.if_mac), force=True)
        cli('rm -rf /opt/rdhcp/%s' % self.name, force=True)
    
    def delete(self):
        self.__delete_namespace__()
        intf = Interface.get(self.if_id)
        intf.ns_id = 0
        intf.ns_name = ''
        intf.update()
        hosts = Host.list(Host.ns_id==self.id)
        for host in hosts: Model.delete(host)
        return Model.delete(self)
    
    def createHost(self, mac, ip, name=''):
        return Host(self, mac, ip, name).create()
    
    def toDict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'pid' : self.pid,
            'if_id' : self.if_id,
            'if_name' : self.if_name,
            'if_mac' : self.if_mac,
            'if_ip' : self.if_ip,
            'net' : self.net,
            'mask' : self.mask,
            'gw' : self.gw,
            'dns' : self.dns,
            'ntp' : self.ntp
        }

@model(db)
class Host(Model):
    
    name = String(256)
    ns_id = Integer()
    mac = String(24)
    ip = String(16)
    
    def __init__(self, ns, mac, ip, name):
        self.ns_id = ns.id
        self.ns_name = ns.name
        self.mac = mac
        self.ip = ip
        self.name = name
    
    def create(self):
        ns = NameSpace.get(self.ns_id)
        hosts = Host.list(Host.ns_id==self.ns_id)
        dhcp_file = 'dhcp-option=1,%s\ndhcp-range=%s,%s\n' % (ns.mask, ns.net, ns.net)
        hosts_file = ''
        if ns.gw != '': dhcp_file += 'dhcp-option=3,%s\n' % (ns.gw)
        if ns.dns != '': dhcp_file += 'dhcp-option=6,%s\n' % (ns.dns)
        if ns.ntp != '': dhcp_file += 'dhcp-option=42,%s\n' % (ns.ntp)
        for host in hosts:
            dhcp_file += 'dhcp-host=%s,%s\n' % (host.mac, host.ip)
            if host.name: hosts_file += '%s    %s\n' % (host.ip, host.name)
        dhcp_file += 'dhcp-host=%s,%s\n' % (self.mac, self.ip)
        if self.name: hosts_file += '%s    %s\n' % (self.ip, self.name)
        with open('/opt/rdhcp/%s/dhcp' % ns.name, 'w') as fd: fd.write(dhcp_file)
        if hosts_file:
            with open('/opt/rdhcp/%s/hosts' % ns.name, 'w') as fd: fd.write(hosts_file)
        cli('ip netns exec %s kill -1 %d' % (ns.name, ns.pid))
        return Model.create(self)
    
    def delete(self):
        Model.delete(self)
        ns = NameSpace.get(self.ns_id)
        hosts = Host.list(Host.ns_id==self.ns_id)
        dhcp_file = 'dhcp-option=1,%s\ndhcp-range=%s,%s\n' % (ns.mask, ns.net, ns.net)
        hosts_file = ''
        if ns.gw != '': dhcp_file += 'dhcp-option=3,%s\n' % (ns.gw)
        if ns.dns != '': dhcp_file += 'dhcp-option=6,%s\n' % (ns.dns)
        if ns.ntp != '': dhcp_file += 'dhcp-option=42,%s\n' % (ns.ntp)
        for host in hosts:
            dhcp_file += 'dhcp-host=%s,%s\n' % (host.mac, host.ip)
            if host.name: hosts_file += '%s    %s\n' % (host.ip, host.name)
        with open('/opt/rdhcp/%s/dhcp' % ns.name, 'w') as fd: fd.write(dhcp_file)
        if hosts_file:
            with open('/opt/rdhcp/%s/hosts' % ns.name, 'w') as fd: fd.write(hosts_file)
        cli('ip netns exec %s kill -1 %d' % (ns.name, ns.pid))
        return self
    
    def toDict(self):
        return {
            'id' : self.id,
            'ns_id' : self.ns_id,
            'mac' : self.mac,
            'ip' : self.ip,
            'name' : self.name
        }
