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

def get_kind(dev):
    rtnl_link_ops = dev.rtnl_link_ops
#     print("%lx" % rtnl_link_ops.value_())
    if rtnl_link_ops.value_():
        kind = dev.rtnl_link_ops.kind
        return kind.string_().decode()

# def print_net_bridge_port(port):

def print_net_bridge(bridge):
    print("\n=== bridge.port_list ===\n")
    i = 1
    for port in list_for_each_entry('struct net_bridge_port', bridge.port_list.address_of_(), 'list'):
        print("%d: %s, flags: %x" % (i, port.dev.name.string_().decode(), port.flags))
        i = i + 1

    print("\n=== bridge.fdb_hash_tbl, struct net_bridge_fdb_entry ===")
    for i, net_bridge_fdb_entry in enumerate(hash(bridge.fdb_hash_tbl, 'struct net_bridge_fdb_entry', 'rhnode')):
#         if not net_bridge_fdb_entry.flags & 1 << prog['BR_FDB_OFFLOADED'].value_():
#             continue
        print("%d: " % i, end='')
        print("key.addr: %s " % mac(net_bridge_fdb_entry.key.addr.addr), end='')
        print("dst port name: %-20s" % net_bridge_fdb_entry.dst.dev.name.string_().decode(), end='')
        print("flag: %lx (BR_FDB_ADDED_BY_EXT_LEARN | BR_FDB_OFFLOADED)" % net_bridge_fdb_entry.flags)

for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    if get_kind(dev) == "bridge":
#         print("state: %x, %x" % (dev.state, prog['__LINK_STATE_NOCARRIER']))
        # ignore docker0
        if not (dev.state & 1 << prog['__LINK_STATE_NOCARRIER'].value_()):
            print("bridge name: %s" % name)
            net_bridge_addr = dev.value_() + prog.type('struct net_device').size
            net_bridge = Object(prog, 'struct net_bridge', address=net_bridge_addr)
            print_net_bridge(net_bridge)
