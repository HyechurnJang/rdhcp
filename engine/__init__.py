
import os
import re
from pygics import rest, Lock
from .core import controller
from .model import Interface, NameSpace, Host

lock = Lock()

@rest('GET', '/find')
def find_host(request, namespace, ip):
    try: return controller.findHost(namespace, ip)
    except Exception as e: return {'error' : str(e)}

@rest('GET', '/status')
def status_resource(request):
    try:
        ret = {
            'interface' : controller.getInterfaces(),
            'namespace' : controller.getNameSpaces(),
            'host' : controller.getHosts(),
            'ntp' : controller.getNTPServers(),
        }
    except Exception as e: ret = {'error' : str(e)}
    return ret

@rest('GET', '/sync')
def sync_resource(request):
    lock.on()
    try:
        ret = {
            'interface' : controller.syncInterfaces(),
            'namespace' : controller.syncNameSpace(),
            'host' : controller.getHosts(),
            'ntp' : controller.syncNTP(),
        }
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('GET', '/mgmt')
def get_if_mgmt(request):
    return {
        'name' : os.environ.get('RDHCP_IF_MGMT'),
        'mac' : os.environ.get('RDHCP_IF_MGMT_MAC'),
        'ip' : os.environ.get('RDHCP_IF_MGMT_IP'),
        'mask' : os.environ.get('RDHCP_IF_MGMT_MASK'),
        'net' : os.environ.get('RDHCP_IF_MGMT_NET'),
        'cidr' : os.environ.get('RDHCP_IF_MGMT_CIDR'),
        'prefix' : os.environ.get('RDHCP_IF_MGMT_PREFIX')
    }

@rest('GET', '/ntp')
def get_ntp(request):
    try: return {'ntp' : controller.getNTPServers()}
    except Exception as e: return {'error' : str(e)}

@rest('POST', '/ntp')
def add_ntp(request):
    try: server = request.data['server']
    except Exception as e: return {'error' : str(e)}
    lock.on()
    try: ret = {'ntp' : controller.addNTPServer(server)}
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('DELETE', '/ntp')
def del_ntp(request, server):
    lock.on()
    try: ret = {'ntp' : controller.delNTPServer(server)}
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('GET', '/interface')
def get_interface(request, interface=None):
    try:
        if interface: return controller.getInterface(interface)
        else: return {'interface' : controller.getInterfaces()}
    except Exception as e: return {'error' : str(e)}

@rest('POST', '/interface')
def set_interface(request):
    try:
        if_p = request.data['interface']
        ip = request.data['ip']
        mask = request.data['mask']
    except Exception as e: return {'error' : str(e)}
    lock.on()
    try: ret = controller.setInterfaceIP(if_p, ip, mask)
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('GET', '/namespace')
def get_namespace(request, namespace=None):
    try:
        if namespace: return controller.getNameSpace(namespace)
        else: return {'namespace' : controller.getNameSpaces()}
    except Exception as e: return {'error' : str(e)}

@rest('POST', '/namespace')
def create_namespace(request):
    try:
        name = request.data['name']
        if_p = request.data['interface']
    except Exception as e: return {'error' : str(e)}
    gw = request.data['gw'] if 'gw' in request.data else ''
    dns = request.data['dns'] if 'dns' in request.data else ''
    ntp = request.data['ntp'] if 'ntp' in request.data else ''
    stt = request.data['dhcp_start'] if 'dhcp_start' in request.data else ''
    end = request.data['dhcp_end'] if 'dhcp_end' in request.data else ''
    lock.on()
    try: ret = controller.createNameSpace(name, if_p, stt, end, gw, dns, ntp)
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('DELETE', '/namespace')
def delete_namespace(request, namespace):
    lock.on()
    try: ret = controller.deleteNameSpace(namespace)
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('GET', '/host')
def get_host(request, param=None):
    try:
        if param:
            if controller.checkMACFormat(param) or param.isdigit(): return controller.getHost(param)
            else: return {'host' : controller.getHosts(param)}
        else: return {'host' : controller.getHosts()}
    except Exception as e: return {'error' : str(e)}
    
@rest('POST', '/host')
def create_host(request):
    try:
        ns_p = request.data['namespace']
        mac = request.data['mac']
        ip = request.data['ip']
    except Exception as e: return {'error' : str(e)}
    name = request.data['name'] if 'name' in request.data else ''
    lock.on()
    try: ret = controller.createHost(ns_p, mac, ip, name)
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('DELETE', '/host')
def delete_host(request, host):
    lock.on()
    try: ret = controller.deleteHost(host)
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret
