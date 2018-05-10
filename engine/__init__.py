
from pygics import rest, Lock
from .core import controller
from .model import Interface, NameSpace, Host

lock = Lock()

@rest('GET', '/sync')
def sync_interfaces(request):
    lock.on()
    controller.syncInterfaces()
    lock.off()
    try: return {'data' : controller.getInterfaces()}
    except Exception as e: return {'error' : str(e)}

@rest('GET', '/interface')
def get_interface(request, intf=None):
    try:
        if intf: return controller.getInterface(intf)
        else: return {'data' : controller.getInterfaces()}
    except Exception as e: return {'error' : str(e)}

@rest('POST', '/interface')
def set_interface(request):
    try:
        if_p = request.data['intf']
        ip = request.data['ip']
        mask = request.data['mask']
    except Exception as e: return {'error' : str(e)}
    lock.on()
    try: ret = controller.setInterfaceIP(if_p, ip, mask)
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('GET', '/namespace')
def get_namespace(request, ns=None):
    try:
        if ns: return controller.getNameSpace(ns)
        else: return {'data' : controller.getNameSpaces()}
    except Exception as e: return {'error' : str(e)}

@rest('POST', '/namespace')
def create_namespace(request):
    try:
        name = request.data['name']
        if_p = request.data['intf']
    except Exception as e: return {'error' : str(e)}
    gw = request.data['gw'] if 'gw' in request.data else ''
    dns = request.data['dns'] if 'dns' in request.data else ''
    ntp = request.data['ntp'] if 'ntp' in request.data else ''
    lock.on()
    try: ret = controller.createNameSpace(name, if_p, gw, dns, ntp)
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('DELETE', '/namespace')
def delete_namespace(request, ns):
    lock.on()
    try: ret = controller.deleteNameSpace(ns)
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret

@rest('GET', '/host')
def get_host(request, h=None):
    try:
        if h: return controller.getHost(h)
        else: return {'data' : controller.getHosts()}
    except Exception as e: return {'error' : str(e)}

@rest('POST', '/host')
def create_host(request):
    try:
        ns_p = request.data['ns']
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
def delete_host(request, h):
    lock.on()
    try: ret = controller.deleteHost(h)
    except Exception as e: ret = {'error' : str(e)}
    lock.off()
    return ret
