#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object
from drgn import cast
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

dev = get_mlx5_core_dev(0)
print(dev.coredev_type)
print(dev.device.kobj.name)

priv = dev.priv
steering = priv.steering
vport_dests = steering.fdb_root_ns.fs_hws_context.hws_pool.vport_dests
print(steering.fdb_root_ns.fs_hws_context.hws_pool.vport_dests)
print("==steering.fdb_root_ns.fs_hws_context.hws_pool.vport_dests==")
for node in radix_tree_for_each(vport_dests.address_of_()):
    action = Object(prog, 'struct mlx5hws_action', address=node[1].value_())
    print("mlx5hws_action %x" % node[1].value_())
    print(action)
# print("==steering.fdb_root_ns.fs_hws_context.hws_pool.vport_vhca_dests==")
# vport_vhca_dests = steering.fdb_root_ns.fs_hws_context.hws_pool.vport_vhca_dests
# for node in radix_tree_for_each(vport_vhca_dests.address_of_()):
#     action = Object(prog, 'struct mlx5hws_action', address=node[1].value_())
#     print(action)

print('')
print("FDB_BYPASS_PATH: %d" % prog['FDB_BYPASS_PATH'])
print("FDB_TC_OFFLOAD:  %d" % prog['FDB_TC_OFFLOAD'])
print("FDB_FT_OFFLOAD:  %d" % prog['FDB_FT_OFFLOAD'])
print("FDB_SLOW_PATH:   %d" % prog['FDB_SLOW_PATH'])
print("FDB_PER_VPORT:   %d" % prog['FDB_PER_VPORT'])

def print_prio(prio, num):
    num_levels = prio.num_levels.value_()
    start_level = prio.start_level.value_()
    prio1 = prio.prio.value_()
    num_ft = prio.num_ft.value_()
#     print("fs_prio %lx" % prio)
#     if num_ft:
    for i in range(num):
        print("\t", end='')
    print("fs_prio %x, num_level: %4d, start_level: %4d, prio: %4d, num_ft: %4d" % \
          (prio, num_levels, start_level, prio1, num_ft))

    if num == 2:
        table_addr = prio.node.children.address_of_()
        for table_node in list_for_each_entry('struct fs_node', table_addr, 'list'):
            for i in range(num):
                print("\t", end='')
            table = cast("struct mlx5_flow_table *", table_node)
            print_table(table)

def print_table(table):
    id = table.id
    max_fte = table.max_fte
    level = table.level
    type = table.type
    print("\tmlx5_flow_table %lx" % table, end='\t')
    print("id: %5x, max_fte: %8x, level: %3d, type: " % \
        (id, max_fte, level), end='')
    print(type)

def print_namespace_level2(ns):
    prio_addr = ns.node.children.address_of_()
    for prio_node in list_for_each_entry('struct fs_node', prio_addr, 'list'):
        prio = cast("struct fs_prio *", prio_node)
        print_prio(prio, 2)

def print_namespace(ns):
    prio_addr = ns.node.children.address_of_()
    for prio_node in list_for_each_entry('struct fs_node', prio_addr, 'list'):
#         print(prio_node)
        prio = cast("struct fs_prio *", prio_node)
#         print(prio)
        if prio.prio == 1:
            print_prio(prio, 0)
            ns_addr = prio.node.children.address_of_()
            for ns_node in list_for_each_entry('struct fs_node', prio_addr, 'list'):
                ns2 = cast("struct mlx5_flow_namespace *", ns_node)
                prio_addr2 = ns2.node.children.address_of_()
                for prio_node2 in list_for_each_entry('struct fs_node', prio_addr2, 'list'):
                    prio2 = cast("struct fs_prio *", prio_node2)
                    print_prio(prio, 1)

if steering.fdb_root_ns:
    fdb_root_ns = steering.fdb_root_ns
    print(fdb_root_ns.mode)
    print("root ft: %lx" % fdb_root_ns.root_ft)
    print("============ fdb_root_ns mlx5_flow_namespace %x ===============" % fdb_root_ns.ns.address_of_())
    print_namespace(fdb_root_ns.ns)
    print('')


sys.exit(0)

offloads = priv.eswitch.fdb_table.offloads
esw_chains_priv = offloads.esw_chains_priv
chains_ht =   esw_chains_priv.chains_ht

for i, chain in enumerate(hash(chains_ht, 'struct fs_chain', 'node')):
#     print(chain)
    print("chain id: %x\nfdb_chain %x" % (chain.id, chain))
    for prio in list_for_each_entry('struct prio', chain.prios_list.address_of_(), 'list'):
        fdb = prio.ft
        next_fdb = prio.next_ft
        miss_group = prio.miss_group
        miss_rule = prio.miss_rule
        print("\n=== chain: %x, prio: %x, level: %x ===" % \
            (prio.key.chain, prio.key.prio, prio.key.level))
        print("prio %lx, ref: %d" % (prio, prio.ref))
        print("next_fdb: %lx, miss_group: %lx, miss_rule: mlx5_flow_handle %lx" % \
            (next_fdb, miss_group, miss_rule))
        table = prio.ft
        flow_table("", table)
