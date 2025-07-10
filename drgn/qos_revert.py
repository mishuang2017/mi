#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

# if esw.qos.refcnt.refs.counter == 0:
#     print("qos is not enabled")
#     exit()

print("\n === esw qos ===\n")
# print("\n === esw.qos.node0 ===\n")
# print(mlx5_esw_sched_node)


# print("\n === mlx5_esw_sched_node ===\n")
# for node in list_for_each_entry('struct mlx5_esw_sched_node', \
#     mlx5_esw_sched_node.list.address_of_(), 'list'):
#     print(node)
 
def print_mac(mac):
    print("mac: %02x:%02x:%02x:%02x:%02x:%02x" % (mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]), end='')

print("\n === vports qos ===\n")

#         SCHED_NODE_TYPE_VPORTS_TSAR,
#         SCHED_NODE_TYPE_VPORT,
#         SCHED_NODE_TYPE_RATE_LIMITER,

SCHED_NODE_TYPE_VPORT          = prog['SCHED_NODE_TYPE_VPORT']
SCHED_NODE_TYPE_VPORTS_TSAR    = prog['SCHED_NODE_TYPE_VPORTS_TSAR']

def type(type):
    if type == SCHED_NODE_TYPE_VPORT:
        return "SCHED_NODE_TYPE_VPORT"
    if type == SCHED_NODE_TYPE_VPORTS_TSAR:
        return "SCHED_NODE_TYPE_VPORTS_TSAR"

def print_mlx5_vport(priv):
    mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
    vports = mlx5_eswitch.vports
    total_vports = mlx5_eswitch.total_vports
    enabled_vports = mlx5_eswitch.enabled_vports

    print("total_vports: %d" % total_vports)
    print("enabled_vports: %d" % enabled_vports)

    uplink_idx = total_vports - 1
    # uplink_vport = vports[uplink_idx]
    # print(vports)

    def print_vport(vport):
        node = vport.qos.sched_node
        if node.value_() == 0:
            return
#         print(vport.devm_port.mlxdevm_rate)
        print("mlx5_vport %x" % vport.address_of_(), end=' ')
        print("vport: %4x, %4d, metadata: %4x" % (vport.vport, vport.vport, vport.metadata), end=' ')
        print_mac(vport.info.mac)
        print("\tdevlink_port %18x" % vport.dl_port.value_(), end=' ')
        print("vport: %5x" % vport.vport, end=' ')
        print("enabled: %x" % vport.enabled.value_())
#         print(vport.qos.sched_node)
        node = vport.qos.sched_node
        print('--- %x ----' % node)
        if node:
            print("sched_node type: %d, ix: %d, esw: %x, tx_max: %d, min_rate: %d" % (node.type, node.ix, node.esw.value_(), node.max_rate, node.min_rate))
            if node.parent:
                print("sched_node.parent: %x, type: %d" % (node.parent, node.parent.type))
        print('')

    for node in radix_tree_for_each(vports.address_of_()):
        mlx5_vport = Object(prog, 'struct mlx5_vport', address=node[1].value_())
#         if mlx5_vport.vport < 4:
        print_vport(mlx5_vport)

def print_nodes(nodes):
    print(" === nodes ===\n")

    for node in list_for_each_entry('struct mlx5_esw_sched_node', nodes.address_of_(), 'entry'):
        print("mlx5_esw_sched_node %x" % node, end='\t')
        if os.path.isdir('/sys/class/net/enp8s0f0/device/sriov/groups'):
            print("group id: %#x" % node.node_id, end='\t')
            print("num_vports: %d" % node.num_vports, end='\t')
            if node.devm.name:
                print("%5s" % node.devm.name.string_().decode(), end='\t')
#                 print(node.devm)
            else:
                print("%5s" % "", end='\t')
        print("type: %d" % node.type, end='\t')
#         print("ix: %d" % node.ix, end='\t')
#         print("node_id: %d" % node.node_id, end='\t')
        print("%s" % node.esw.dev.device.kobj.name.string_().decode(), end='\t')
        print("max_rate: %d, min_rate: %d, bw_share: %d" % (node.max_rate, node.min_rate, node.bw_share), end=' ');
        print("parent %x" % node.parent.value_())
        for node2 in list_for_each_entry('struct mlx5_esw_sched_node', node.children.address_of_(), 'entry'):
            if node2.type.value_() == SCHED_NODE_TYPE_VPORT:
                vport = node2.vport
                print("\t---------------")
#                 print("\tnode: %x, type: %d, vport: %d" % (node2.value_(), type(node2.type), vport.vport), end=' ')
                print("\tmlx5_esw_sche_node %x, type: %d, vport: %d" % (node2.value_(), node2.type, vport.vport), end=' ')
                print("\t%s" % vport.dev.device.kobj.name.string_().decode())
            else:
                print("\tchild group mlx5_esw_sche_node %x, type: %d" % (node2.value_(), node2.type))
        print("")
print("\n === vports qos port 1 ===\n")

mlx5e_priv = get_mlx5_pf0()
print_mlx5_vport(mlx5e_priv)

esw = mlx5e_priv.mdev.priv.eswitch
print("esw.qos.refcnt.refs.counter: %d" % esw.qos.refcnt.refs.counter)
print_nodes(esw.qos.domain.nodes)

print("\n === vports qos port 2 ===\n")

mlx5e_priv = get_mlx5_pf1()
print_mlx5_vport(mlx5e_priv)

esw = mlx5e_priv.mdev.priv.eswitch
   
# print_domain(esw)
