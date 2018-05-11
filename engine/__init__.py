
import re
from pygics import rest, Lock
from .core import controller
from .model import Interface, NameSpace, Host

lock = Lock()

@rest('GET', '/find')
def find_host(request, namespace, ip):
    try: return controller.findHost(namespace, ip)
    except Exception as e: return {'error' : str(e)}

@rest('GET', '/sync')
def sync_interfaces(request):
    lock.on()
    try: ret = {'data' : controller.syncInterfaces()}
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('GET', '/mgmt')
def get_if_mgmt(request):
    return {'data' : controller.if_mgmt}

@rest('POST', '/mgmt')
def set_if_mgmt(request):
    try: if_mgmt = request.data['interface']
    except Exception as e: return {'error' : str(e)}
    lock.on()
    try: ret = {'data' : controller.setIfMgmt(if_mgmt)}
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('GET', '/interface')
def get_interface(request, interface=None):
    try:
        if interface: return controller.getInterface(interface)
        else: return {'data' : controller.getInterfaces()}
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
        else: return {'data' : controller.getNameSpaces()}
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
            else: return {'data' : controller.getHosts(param)}
        else: return {'data' : controller.getHosts()}
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
