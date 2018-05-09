
from pygics import rest
from .core import controller
from .model import Interface, NameSpace, Host

@rest('GET', '/interface/sync')
def sync_interfaces(request):
    controller.syncInterface()
    return {'data' : [intf.toDict() for intf in Interface.list()]}

@rest('GET', '/interface')
def get_interfaces(request):
    return {'data' : [intf.toDict() for intf in Interface.list()]}

@rest('GET', '/interface/detail')
def get_interface(request, if_name):
    intf = Interface.one(Interface.name==if_name)
    if intf: return intf.toDict()
    else: {'error' : 'invalid parameter'}

@rest('POST', '/interface/conf')
def conf_interface(request, if_name):
    try:
        ip = request.data['ip']
        mask = request.data['mask']
    except Exception as e: return {'error' : str(e)}
    try: intf = controller.setInterface(if_name, ip, mask)
    except Exception as e: return {'error' : str(e)}
    if intf: return intf.toDict()
    else: return {'error' : 'invalid parameter'}

@rest('GET', '/namespace')
def get_namespaces(request):
    return {'data' : [ns.toDict() for ns in NameSpace.list()]}

@rest('POST', '/namespace')
def create_namespace(request):
    try:
        ns_name = request.data['ns_name']
        if_name = request.data['if_name']
    except Exception as e: return {'error' : str(e)}
    gw = request.data['gw'] if 'gw' in request.data else ''
    dhcp = request.data['dhcp'] if 'dhcp' in request.data else ''
    dns = request.data['dns'] if 'dns' in request.data else ''
    ntp = request.data['ntp'] if 'ntp' in request.data else ''
    ns = controller.createNamespace(ns_name, if_name, gw, dhcp, dns, ntp)
    if ns: return ns.toDict()
    else: return {'error' : 'invalid parameter'}

@rest('DELETE', '/namespace')
def delete_namespace(request, ns_name):
    ns = NameSpace.one(NameSpace.name==ns_name)
    if not ns: return {'error' : 'non exist namespace'}
    ns = controller.deleteNamespace(ns.name, ns.intf)
    if ns: return ns.toDict()
    else: return {'error', 'invalid parameter'}
