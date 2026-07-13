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

SCHED_NODE_TYPE_ROOT            = prog['SCHED_NODE_TYPE_ROOT']
SCHED_NODE_TYPE_VPORTS_TSAR     = prog['SCHED_NODE_TYPE_VPORTS_TSAR']
SCHED_NODE_TYPE_VPORT           = prog['SCHED_NODE_TYPE_VPORT']
SCHED_NODE_TYPE_VPORT_TC        = prog['SCHED_NODE_TYPE_VPORT_TC']
SCHED_NODE_TYPE_VPORTS_TC_TSAR  = prog['SCHED_NODE_TYPE_VPORTS_TC_TSAR']
SCHED_NODE_TYPE_TC_ARBITER_TSAR = prog['SCHED_NODE_TYPE_TC_ARBITER_TSAR']

def type(type):
    if type == SCHED_NODE_TYPE_ROOT:
        return "SCHED_NODE_TYPE_ROOT"
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
        node = vport.qos.sched_node
        is_tc_arbiter = node.type == SCHED_NODE_TYPE_TC_ARBITER_TSAR
        if not is_tc_arbiter:
            print("sched_node type: %s, ix: %d, esw: %x, tx_max: %d, min_rate: %d" % (type(node.type), node.ix, node.esw.value_(), node.max_rate, node.min_rate))
            print("vport.qos.sched_node.parent: %x, type: %s" % (node.parent, type(node.parent.type)))
            print("vport.qos.sched_node.parent.parent: %x" % (node.parent.parent))

        if is_tc_arbiter:
            print("sched_node type: %s, ix: %d, max_rate: %d, min_rate: %d" % \
                (type(node.type), node.ix, node.max_rate, node.min_rate))
            if node.parent.value_():
                print("vport.qos.sched_node.parent: %x, type: %s" % \
                    (node.parent, type(node.parent.type)))
            for i in range(2):
                tc_node = vport.qos.sched_nodes[i]
                print("%-35s" % type(tc_node.type), end=' ')
                print("node: %x" % tc_node.value_(), end=' ')
                print("tc: %d" % tc_node.tc, end=' ')
                print('')
                print("%-35s" % type(tc_node.parent.type), end=' ')
                print("parent: %x" % tc_node.parent.value_(), end=' ')
                print("tc: %d" % tc_node.parent.tc, end=' ')
                print("bw_share: %d" % tc_node.parent.bw_share, end=' ')
                print("max_rate: %d" % tc_node.parent.max_rate, end=' ')
                print("min_rate: %d" % tc_node.parent.min_rate, end=' ')
                print("user_bw_share: %d" % tc_node.parent.user_bw_share, end=' ')
                print('')
                if tc_node.parent:
                    print("%-35s" % type(tc_node.parent.parent.type), end=' ')
                    print("parent parent: %x" % tc_node.parent.parent.value_(), end=' ')
                print('\n----------------------------------------------')
        print('')

    for node in radix_tree_for_each(vports.address_of_()):
        mlx5_vport = Object(prog, 'struct mlx5_vport', address=node[1].value_())
#         if mlx5_vport.vport < 4:
        print_vport(mlx5_vport)

def find_devlink_rate_name(node):
    """Return the rate name (e.g. 'g1') for a sched_node via devlink or mlxdevm, or None."""
    node_ix = int(node.ix)

    shd = node.esw.dev.shd
    if shd.value_():
        for rate in list_for_each_entry('struct devlink_rate', shd.rate_list.address_of_(), 'list'):
            if not rate.priv.value_():
                continue
            sched_node = Object(prog, 'struct mlx5_esw_sched_node *', value=rate.priv.value_())
            if sched_node.ix == node_ix:
                return rate.name.string_().decode()

    try:
        shd_mlxdevm = node.esw.dev.shd_mlxdevm
        if shd_mlxdevm.value_():
            for rate in list_for_each_entry('struct mlxdevm_rate', shd_mlxdevm.rate_list.address_of_(), 'list'):
                if not rate.priv.value_():
                    continue
                sched_node = Object(prog, 'struct mlx5_esw_sched_node *', value=rate.priv.value_())
                if sched_node.ix == node_ix:
                    return rate.name.string_().decode()
    except AttributeError:
        pass

    return None

def print_node(node, indent=0):
    prefix = '\t' * indent
    node_type = type(node.type)
    dev_name = node.esw.dev.device.kobj.name.string_().decode()
    rate_name = find_devlink_rate_name(node)
    rate_str = ("  devlink_rate: %s" % rate_name) if rate_name else ""
    print("%snode: %x  type: %s  ix: %d  dev: %s  max_rate: %d  min_rate: %d  bw_share: %d  parent: %x%s" % (
        prefix, node.value_(), node_type, node.ix, dev_name,
        node.max_rate, node.min_rate, node.bw_share,
        node.parent.value_() if node.parent.value_() else 0,
        rate_str))
    if node.type == SCHED_NODE_TYPE_VPORT:
        vport = node.vport
        print("%s  vport: %d  %s" % (prefix, vport.vport,
              vport.dev.device.kobj.name.string_().decode()))
    for child in list_for_each_entry('struct mlx5_esw_sched_node', node.children.address_of_(), 'entry'):
        print_node(child, indent + 1)

def print_qos_tree(esw):
    root = esw.qos.root
    if not root.value_():
        print("  qos.root is NULL (QoS not initialized)")
        return
    print("\n === qos tree (root: %x  ix: %d) ===\n" % (root.value_(), root.ix))
    for node in list_for_each_entry('struct mlx5_esw_sched_node', root.children.address_of_(), 'entry'):
        print_node(node, indent=1)

print("\n === vports qos port 1 ===\n")

mlx5e_priv = get_mlx5_pf0()
print_mlx5_vport(mlx5e_priv)

esw = mlx5e_priv.mdev.priv.eswitch
print_qos_tree(esw)

print("\n === vports qos port 2 ===\n")

mlx5e_priv = get_mlx5_pf1()
print_mlx5_vport(mlx5e_priv)

esw = mlx5e_priv.mdev.priv.eswitch
print_qos_tree(esw)

