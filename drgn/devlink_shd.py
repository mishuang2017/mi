#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

shd_list = prog['shd_list']
# print(shd_list)

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

def print_nodes(nodes):
    print(" === mlx5_shd.qos_nodes ===\n")

    for node in list_for_each_entry('struct mlx5_esw_sched_node', nodes.address_of_(), 'entry'):
        print("node: %x" % node, end='\t')
        print("type: %s" % type(node.type), end='\t')
#         print("ix: %d" % node.ix, end='\t')
        print("%s" % node.esw.dev.device.kobj.name.string_().decode(), end='\t')
        print("max_rate: %d, min_rate: %d, bw_share: %d" % (node.max_rate, node.min_rate, node.bw_share), end=' ');
#         print("parent %x" % node.parent.value_(), end=' ')
        print("leve: %d" % node.level)
        for node2 in list_for_each_entry('struct mlx5_esw_sched_node', node.children.address_of_(), 'entry'):
            if node2.type.value_() == SCHED_NODE_TYPE_VPORT:
                vport = node2.vport
                print("\t---------------")
                print("\tnode: %x, type: %s, vport: %d" % (node2.value_(), type(node2.type), vport.vport), end=' ')
                print("\t%s" % vport.dev.device.kobj.name.string_().decode(), end=' ')
                print("\tleve: %d" % node.level)
            elif node2.type == SCHED_NODE_TYPE_VPORTS_TC_TSAR:
                if node2.bw_share == 1:
                    continue
                print("\tnode: %x, type: %s, ix: %d, tc: %d, max_rate: %d, min_rate: %d, bw_share: %d, level: %d" % \
                    (node2.value_(), type(node2.type), node2.ix, node2.tc, node2.max_rate, \
                    node2.min_rate, node2.bw_share, node2.level))
                for node3 in list_for_each_entry('struct mlx5_esw_sched_node', node2.children.address_of_(), 'entry'):
                    print("\t\tnode: %x, type: %s, ix: %d, tc: %d, max_rate: %d, min_rate: %d, bw_share: %d, vport: %x (%d), leve: %d" % \
                        (node3.value_(), type(node3.type), node3.ix, node3.tc, node3.max_rate, node3.min_rate, node3.bw_share, \
                        node3.vport.value_(), node3.vport.vport, node3.level))
            elif node2.type == SCHED_NODE_TYPE_TC_ARBITER_TSAR or node2.type == SCHED_NODE_TYPE_VPORTS_TSAR:
                print("\t---------------")
                print("\tnode: %x, type: %s, ix: %d, max_rate: %d, min_rate: %d, bw_share: %d, vport: %x (%d)" % \
                    (node2.value_(), type(node2.type), node2.ix, node2.max_rate, node2.min_rate, node2.bw_share, \
                    node2.vport.value_(), node2.vport.vport), end=' ')
                print("\tleve: %d" % node2.level)
            else:
                print(node)
        print("")


for mlx5_shd in list_for_each_entry('struct mlx5_shd', shd_list.address_of_(), 'list'):
    print(mlx5_shd)
    print("mlx5_shd.faux_dev.dev.driver_data", end=' ')
    print(mlx5_shd.faux_dev.dev.driver_data)
    devlink = container_of(mlx5_shd, "struct devlink", "priv")
#     print(devlink.dev.kobj)
    print_nodes(mlx5_shd.qos_nodes)
    print("===mlx5_shd.dev_list===")
    for dev in list_for_each_entry('struct mlx5_core_dev', mlx5_shd.dev_list.address_of_(), 'shd_list'):
        print("\tmlx5_core_dev %#x, %s, mlx5_shd %#x" % (dev, dev.device.kobj.name.string_().decode(), dev.shd))

exit(0)

devlink_rels = prog['devlink_rels']
for node in radix_tree_for_each(devlink_rels.address_of_()):
    print('-------------------------------------')
    rel = Object(prog, 'struct devlink_rel', address=node[1].value_())
    print("rel.index: %d, rel.devlink_index: %d, nested_in.devlink_index: %d" % (rel.index, rel.devlink_index, rel.nested_in.devlink_index))
#     print(rel)
