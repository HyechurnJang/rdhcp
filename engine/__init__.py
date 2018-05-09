
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
def conf_interface(request, if_name, ip, mask):
    try: intf = controller.setInterface(if_name, ip, mask)
    except Exception as e: return {'error' : str(e)}
    if intf: return intf.toDict()
    else: return {'error' : 'invalid parameter'}

@rest('GET', '/namespace')
def get_namespaces(request):
    return {'data' : [ns.toDict() for ns in NameSpace.list()]}

@rest('POST', '/namespace')
def create_namespace(request, ns_name, if_name, gw='', dhcp='', dns='', ntp=''):
    ns = controller.createNamespace(ns_name, if_name, gw, dhcp, dns, ntp)
    if ns: return ns.toDict()
    else: return {'error' : 'invalid parameter'}

@rest('DELETE', '/namespace')
def delete_namespace(request, ns_name, if_name):
    ns = controller.deleteNamespace(ns_name, if_name)
    if ns: return ns.toDict()
    else: return {'error', 'invalid parameter'}
