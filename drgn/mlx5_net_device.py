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
        print("%15s " % ipv4(socket.ntohl(dev.ip_ptr.ifa_list.ifa_address.value_())), end="")
    else:
        print("%15s " % "", end="")

def print_kind(dev):
    rtnl_link_ops = dev.rtnl_link_ops
#     print("%lx" % rtnl_link_ops.value_())
    if rtnl_link_ops.value_():
        kind = dev.rtnl_link_ops.kind
        print("%15s" % kind.string_().decode(), end='')

for x, dev in enumerate(get_netdevs()):
#     addr = 0xffff93e6b7e00000
#     dev = Object(prog, 'struct net_device', address=addr)
    name = dev.name.string_().decode()
    addr = dev.value_()
#     if "enp" in name:
    netdev_ops = address_to_name(hex(dev.netdev_ops.value_()))
    if "mlx5" not in netdev_ops:
        continue
    print("%5i%20s%20x" % (dev.ifindex, name, addr), end="\t")
    print_ip_address(dev)
    netdev_ops = print("dev.netdev_ops: %s" % netdev_ops, end='\t')
#     print("%10x\t" % dev.priv_flags, end='\t')
#     count = get_pcpu_refcnt(dev)
#     print("%10d" % count, end='\t')
#     print_kind(dev)
#     mlx5e_priv_addr = dev.value_() + prog.type('struct net_device').size
#     mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)
#     print("%x" % mlx5e_priv.fs.tc.ct.value_(), end='\t')
#     print("%x" % mlx5e_priv.dfs_root.value_())
    print("")
