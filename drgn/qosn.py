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

SCHED_NODE_TYPE_VPORTS_TSAR                 = prog['SCHED_NODE_TYPE_VPORTS_TSAR']
SCHED_NODE_TYPE_VPORT                       = prog['SCHED_NODE_TYPE_VPORT']
SCHED_NODE_TYPE_VPORT_TC                    = prog['SCHED_NODE_TYPE_VPORT_TC']
SCHED_NODE_TYPE_VPORTS_TC_TSAR              = prog['SCHED_NODE_TYPE_VPORTS_TC_TSAR']
SCHED_NODE_TYPE_TC_ARBITER_TSAR             = prog['SCHED_NODE_TYPE_TC_ARBITER_TSAR']
SCHED_NODE_TYPE_VPORTS_AND_TC_ARBITERS_TSAR = prog['SCHED_NODE_TYPE_VPORTS_AND_TC_ARBITERS_TSAR']

def type(type):
    if type == SCHED_NODE_TYPE_VPORTS_TSAR:
        return "SCHED_NODE_TYPE_VPORTS_TSAR"
    if type == SCHED_NODE_TYPE_VPORT:
        return "SCHED_NODE_TYPE_VPORT"
    if type == SCHED_NODE_TYPE_VPORT_TC:
        return "SCHED_NODE_TYPE_VPORT_TC"
    if type == SCHED_NODE_TYPE_VPORTS_TC_TSAR:
        return "SCHED_NODE_TYPE_VPORTS_TC_TSAR"
    if type == SCHED_NODE_TYPE_TC_ARBITER_TSAR:
        return "SCHED_NODE_TYPE_TC_ARBITER_TSAR"
    if type == SCHED_NODE_TYPE_VPORTS_AND_TC_ARBITERS_TSAR:
        return "SCHED_NODE_TYPE_VPORTS_AND_TC_ARBITERS_TSAR"

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
        print("mlx5_vport %x" % vport.address_of_(), end=' ')
        print("vport: %4x, %4d, metadata: %4x" % (vport.vport, vport.vport, vport.metadata), end=' ')
        print_mac(vport.info.mac)
        print("\tdevlink_port %18x" % vport.dl_port.value_(), end=' ')
        print("vport: %5x" % vport.vport, end=' ')
        print("enabled: %x" % vport.enabled.value_(), end=' ')
        print(vport.qos)
        if not vport.qos.tc.arbiter_node:
            node = vport.qos.sched_node
            print("sched_node type: %s, ix: %d, esw: %x" % (type(node.type), node.ix, node.esw.value_()))
            print("vport.qos.sched_node.parent: %x, type: %s" % (node.parent, type(node.parent.type)))
            print("vport.qos.sched_node.parent.parent: %x" % (node.parent.parent))

        if vport.qos.tc.arbiter_node:
            print("sched_node type: %s, ix: %d" % (type(vport.qos.sched_node.type), vport.qos.sched_node.ix))
            if vport.qos.sched_node.parent.value_():
                print("vport.qos.sched_node.parent: %x, type: %s" % \
                    (vport.qos.sched_node.parent, type(vport.qos.sched_node.parent.type)))
            for i in range(2):
                node = vport.qos.tc.sched_nodes[i]
                print("%-35s" % type(node.type), end=' ')
                print("node: %x" % node.value_(), end=' ')
                print("tc: %d" % node.tc, end=' ')
                print('')
                print("%-35s" % type(node.parent.type), end=' ')
                print("parent: %x" % node.parent.value_(), end=' ')
                print("tc: %d" % node.parent.tc, end=' ')
                print("bw_share: %d" % node.parent.bw_share, end=' ')
                print('')
                if node.parent:
                    print("%-35s" % type(node.parent.parent.type), end=' ')
                    print("parent parent: %x" % node.parent.parent.value_(), end=' ')
                print('\n----------------------------------------------')
        print('')

    for node in radix_tree_for_each(vports.address_of_()):
        mlx5_vport = Object(prog, 'struct mlx5_vport', address=node[1].value_())
#         if mlx5_vport.vport < 4:
        print_vport(mlx5_vport)

def print_domain(esw):
    print("\n === groups ===\n")
    for node in list_for_each_entry('struct mlx5_esw_sched_node', esw.qos.domain.nodes.address_of_(), 'entry'):
        print("node: %x" % node, end='\t')
        if os.path.isdir('/sys/class/net/enp8s0f0/device/sriov/groups'):
            print("group id: %#x" % node.group_id, end='\t')
            print("num_vports: %d" % node.num_vports, end='\t')
            if node.devm.name:
                print("%5s" % node.devm.name.string_().decode(), end='\t')
            else:
                print("%5s" % "", end='\t')
        print("type: %s" % type(node.type), end='\t')
#         print("ix: %d" % node.ix, end='\t')
#         print("group_id: %d" % node.group_id, end='\t')
        print("%s" % node.esw.dev.device.kobj.name.string_().decode(), end='\t')
        print("max_rate: %d, min_rate: %x, bw_share: %d" % (node.max_rate, node.min_rate, node.bw_share), end=' ');
        print("parent %x" % node.parent.value_())
        print(node.devm)
        for node2 in list_for_each_entry('struct mlx5_esw_sched_node', node.children.address_of_(), 'entry'):
            if node2.type.value_() == SCHED_NODE_TYPE_VPORT:
                vport = node2.vport
                print("\t---------------")
                print("\tnode: %x, type: %s, vport: %d" % (node2.value_(), type(node2.type), vport.vport), end=' ')
                print("\t%s" % vport.dev.device.kobj.name.string_().decode())
            elif node2.type == SCHED_NODE_TYPE_VPORTS_TC_TSAR:
                print("\tnode: %x, type: %s, ix: %d, tc: %d, max_rate: %d, min_rate: %x, bw_share: %d" % \
                    (node2.value_(), type(node2.type), node2.ix, node2.tc, node2.max_rate, \
                    node2.min_rate, node2.bw_share))
                for node3 in list_for_each_entry('struct mlx5_esw_sched_node', node2.children.address_of_(), 'entry'):
                    print("\t\tnode: %x, type: %s, ix: %d, tc: %d, max_rate: %d, min_rate: %x, bw_share: %d, vport: %x" % \
                        (node3.value_(), type(node3.type), node3.ix, node3.tc, node3.max_rate, node3.min_rate, node3.bw_share, \
                        node3.vport.value_()))
            elif node2.type == SCHED_NODE_TYPE_TC_ARBITER_TSAR:
                print("\t---------------")
                print("\tnode: %x, type: %s, ix: %d, tc: %d, max_rate: %d, min_rate: %x, bw_share: %d, vport: %x" % \
                    (node2.value_(), type(node2.type), node2.ix, node2.tc, node2.max_rate, node2.min_rate, node2.bw_share, \
                    node2.vport.value_()))
print("\n === vports qos port 1 ===\n")

mlx5e_priv = get_mlx5_pf0()
print_mlx5_vport(mlx5e_priv)

esw = mlx5e_priv.mdev.priv.eswitch
print_domain(esw)

print("\n === vports qos port 2 ===\n")

mlx5e_priv = get_mlx5_pf1()
print_mlx5_vport(mlx5e_priv)

SCHED_NODE_TYPE_VPORTS_TC_TSAR = prog['SCHED_NODE_TYPE_VPORTS_TC_TSAR']

esw = mlx5e_priv.mdev.priv.eswitch
   
# print_domain(esw)
