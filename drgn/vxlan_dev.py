#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

# TODO: multiple address
def print_ip_address(dev):
    ifa_list = dev.ip_ptr.ifa_list
    if ifa_list:
        print("%15s" % ipv4(socket.ntohl(dev.ip_ptr.ifa_list.ifa_address.value_())), end="")
    else:
        print("%15s" % "", end="")

def get_kind(dev):
    rtnl_link_ops = dev.rtnl_link_ops
#     print("%lx" % rtnl_link_ops.value_())
    if rtnl_link_ops.value_():
        kind = dev.rtnl_link_ops.kind.string_().decode()
        return kind
    return ""
    

for x, dev in enumerate(get_netdevs()):
#     addr = 0xffff93e6b7e00000
#     dev = Object(prog, 'struct net_device', address=addr)
    name = dev.name.string_().decode()
#     if name != "enp8s0f2":
#         continue
    addr = dev.value_()
#     if "enp" in name:
    kind = get_kind(dev)
    if kind != "vxlan":
        continue
    print("%5i%20s%20x\t" % (dev.ifindex, name, addr), end="")
    print_ip_address(dev)
    print("%10x\t" % dev.priv_flags, end='\t')
    count = get_pcpu_refcnt(dev)
    print("%10d" % count, end='')
    print("")
    vxlan_dev_addr = addr + prog.type('struct net_device').size
    vxlan_dev = Object(prog, 'struct vxlan_dev', address=vxlan_dev_addr)
    print(vxlan_dev.cfg)


