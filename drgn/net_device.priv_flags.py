#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

IFF_OVS_DATAPATH = prog['IFF_OVS_DATAPATH']
IFF_BRIDGE_PORT = prog['IFF_BRIDGE_PORT']
IFF_OPENVSWITCH = prog['IFF_OPENVSWITCH']
print("IFF_OVS_DATAPATH: %lx" % IFF_OVS_DATAPATH)
print("IFF_BRIDGE_PORT: %lx" % IFF_BRIDGE_PORT)
print("IFF_OPENVSWITCH: %lx" % IFF_OPENVSWITCH)

for x, dev in enumerate(lib.get_netdevs()):
    name = dev.name.string_().decode()
    addr = dev.value_()
    priv_flags = dev.priv_flags
    print("%20s%20x\t" % (name, addr), end="")
    print("priv_flags: %lx" % priv_flags)
