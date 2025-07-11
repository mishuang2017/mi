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
#         SCHED_NODE_TYPE_VPORT_TC,
#         SCHED_NODE_TYPE_VPORTS_TC_TSAR,
#         SCHED_NODE_TYPE_TC_ARBITER_TSAR,

SCHED_NODE_TYPE_VPORTS_TSAR     = prog['SCHED_NODE_TYPE_VPORTS_TSAR']
SCHED_NODE_TYPE_VPORT           = prog['SCHED_NODE_TYPE_VPORT']
SCHED_NODE_TYPE_RATE_LIMITER    = prog['SCHED_NODE_TYPE_RATE_LIMITER']
SCHED_NODE_TYPE_VPORT_TC        = prog['SCHED_NODE_TYPE_VPORT_TC']
SCHED_NODE_TYPE_VPORTS_TC_TSAR  = prog['SCHED_NODE_TYPE_VPORTS_TC_TSAR']
SCHED_NODE_TYPE_TC_ARBITER_TSAR = prog['SCHED_NODE_TYPE_TC_ARBITER_TSAR']

def type(type):
    if type == SCHED_NODE_TYPE_VPORTS_TSAR:
        return "SCHED_NODE_TYPE_VPORTS_TSAR"
    if type == SCHED_NODE_TYPE_VPORT:
        return "SCHED_NODE_TYPE_VPORT"
    if type == SCHED_NODE_TYPE_RATE_LIMITER:
        return "SCHED_NODE_TYPE_RATE_LIMITER"
    if type == SCHED_NODE_TYPE_VPORT_TC:
        return "SCHED_NODE_TYPE_VPORT_TC"
    if type == SCHED_NODE_TYPE_VPORTS_TC_TSAR:
        return "SCHED_NODE_TYPE_VPORTS_TC_TSAR"
    if type == SCHED_NODE_TYPE_TC_ARBITER_TSAR:
        return "SCHED_NODE_TYPE_TC_ARBITER_TSAR"

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
        print("enabled: %x" % vport.enabled.value_())
        print(vport.qos)
        node = vport.qos.sched_node
        print('-------')
        if node:
            print("sched_node: %x, type: %s, ix: %d, esw: %x, tx_max: %d, min_rate: %d, level: %d" % \
                (node, type(node.type), node.ix, node.esw.value_(), node.max_rate, node.min_rate, node.level))
            print("sched_node.parent: %x, type: %s, ix: %d, level: %d" % \
                (node.parent, type(node.parent.type), node.parent.ix, node.parent.level))

        if vport.qos.sched_nodes:
            print('-------')
            print("vport.qos.sched_node.children:")
            i = 0
            for node in list_for_each_entry('struct mlx5_esw_sched_node', vport.qos.sched_node.children.address_of_(), 'entry'):
                print("%-35s" % type(node.type), end=' ')
                print("node: %x" % node.value_(), end=' ')
                print("tc: %d" % node.tc, end=' ')
                print("ix: %d" % node.ix, end=' ')
                print("leve: %d" % node.level, end=' ')
                print('')
                i += 1
                if i == 2:
                    break
            if i == 0:
                print("\tno child")
            print('-------')
            for i in range(2):
                node = vport.qos.sched_nodes[i]
                print("vports.qos.sched_nods[%d]" % i, end=' ')
                print("%-35s" % type(node.type), end=' ')
                print("node: %x" % node.value_(), end=' ')
                print("tc: %d" % node.tc, end=' ')
                print("ix: %d" % node.ix, end=' ')
                print('')
                print("%-35s" % type(node.parent.type), end=' ')
                print("parent: %x" % node.parent.value_(), end=' ')
                print("tc: %d" % node.parent.tc, end=' ')
#                 print("user_bw_share: %d" % node.parent.user_bw_share, end=' ')
                print("bw_share: %d" % node.parent.bw_share, end=' ')
                print("max_rate: %d" % node.parent.max_rate, end=' ')
                print("min_rate: %d" % node.parent.min_rate, end=' ')
                print("leve: %d" % node.level, end=' ')
                print('')
                if node.parent:
                    print("%-35s" % type(node.parent.parent.type), end=' ')
                    print("parent parent: %x" % node.parent.parent.value_())
                print('-----------------------------------------------------------------------------------------------')
        print('')

    for node in radix_tree_for_each(vports.address_of_()):
        mlx5_vport = Object(prog, 'struct mlx5_vport', address=node[1].value_())
#         if mlx5_vport.vport < 4:
        print_vport(mlx5_vport)

def print_nodes(nodes):
    print(" === groups ===\n")

    for node in list_for_each_entry('struct mlx5_esw_sched_node', nodes.address_of_(), 'entry'):
        print("node: %x" % node, end='\t')
        print("type: %s" % type(node.type), end='\t')
#         print("ix: %d" % node.ix, end='\t')
        print("%s" % node.esw.dev.device.kobj.name.string_().decode(), end='\t')
        print("max_rate: %d, min_rate: %d, bw_share: %d" % (node.max_rate, node.min_rate, node.bw_share), end=' ');
        print("parent %x" % node.parent.value_(), end=' ')
        print("leve: %d" % node.level)
        for node2 in list_for_each_entry('struct mlx5_esw_sched_node', node.children.address_of_(), 'entry'):
            if node2.type.value_() == SCHED_NODE_TYPE_VPORT:
                vport = node2.vport
                print("\t---------------")
                print("\tnode: %x, type: %s, vport: %d" % (node2.value_(), type(node2.type), vport.vport), end=' ')
                print("\t%s" % vport.dev.device.kobj.name.string_().decode(), end=' ')
                print("\tleve: %d" % node.level)
            elif node2.type == SCHED_NODE_TYPE_VPORTS_TC_TSAR:
                print("\tnode: %x, type: %s, ix: %d, tc: %d, max_rate: %d, min_rate: %d, bw_share: %d, level: %d" % \
                    (node2.value_(), type(node2.type), node2.ix, node2.tc, node2.max_rate, \
                    node2.min_rate, node2.bw_share, node2.level))
                for node3 in list_for_each_entry('struct mlx5_esw_sched_node', node2.children.address_of_(), 'entry'):
                    print("\t\tnode: %x, type: %s, ix: %d, tc: %d, max_rate: %d, min_rate: %d, bw_share: %d, vport: %x" % \
                        (node3.value_(), type(node3.type), node3.ix, node3.tc, node3.max_rate, node3.min_rate, node3.bw_share, \
                        node3.vport.value_()))
            elif node2.type == SCHED_NODE_TYPE_TC_ARBITER_TSAR or node2.type == SCHED_NODE_TYPE_VPORTS_TSAR:
                print("\t---------------")
                print("\tnode: %x, type: %s, ix: %d, max_rate: %d, min_rate: %d, bw_share: %d, vport: %x" % \
                    (node2.value_(), type(node2.type), node2.ix, node2.max_rate, node2.min_rate, node2.bw_share, \
                    node2.vport.value_()), end=' ')
                print("\tleve: %d" % node2.level)
            else:
                print(node)
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

SCHED_NODE_TYPE_VPORTS_TC_TSAR = prog['SCHED_NODE_TYPE_VPORTS_TC_TSAR']

esw = mlx5e_priv.mdev.priv.eswitch
   
# print_domain(esw)
