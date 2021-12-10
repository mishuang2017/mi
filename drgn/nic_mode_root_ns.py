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

dev = get_mlx5_core_dev(2)
print(dev.coredev_type)
print(dev.device.kobj.name)

priv = dev.priv
steering = priv.steering
# print(steering)

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
        if prio.prio == prog['MLX5_FLOW_NAMESPACE_KERNEL'].value_():
            print_prio(prio, 0)
            ns = list_first_entry(prio_node.children, "struct mlx5_flow_namespace", "node.list")
            print("\tmlx5_flow_namespace %x" % ns)
            print_namespace_level2(ns)

root_ns = steering.root_ns
print('')
print("============ root_ns mlx5_flow_namespace %x ===============\n" % root_ns)
print_namespace(root_ns.ns)

# for nic mode, both fdb_root_ns and fdb_sub_ns are NULL
# the flow tables are saved in mlx5_fs_chains samed as esw mode.

sys.exit(0)

mlx5e_priv = get_mlx5e_priv("enp8s0f2")
mlx5_fs_chains = mlx5e_priv.fs.tc.chains
# print(mlx5_fs_chains.chains_ht)

for i, chain in enumerate(hash(mlx5_fs_chains.chains_ht, 'struct fs_chain', 'node')):
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

#
# in .bashrc, use function tc_nic to test it.
#
# for nic mode, The namespace is MLX5_FLOW_NAMESPACE_KERNEL. The prio is assigned based on
# the sequence, so it is 4.
# In mlx5_get_flow_namespace(), get the first namespace of that prio.
# There are two prios.
#
# } root_fs = {
#         .type = FS_TYPE_NAMESPACE,
#         .ar_size = 7,
#           .children = (struct init_tree_node[]){
#                   ADD_PRIO(0, BY_PASS_MIN_LEVEL, 0, FS_CHAINING_CAPS,
#                            ADD_NS(MLX5_FLOW_TABLE_MISS_ACTION_DEF,
#                                   ADD_MULTIPLE_PRIO(MLX5_BY_PASS_NUM_PRIOS,
#                                                     BY_PASS_PRIO_NUM_LEVELS))),
#                   ADD_PRIO(0, LAG_MIN_LEVEL, 0, FS_CHAINING_CAPS,
#                            ADD_NS(MLX5_FLOW_TABLE_MISS_ACTION_DEF,
#                                   ADD_MULTIPLE_PRIO(LAG_NUM_PRIOS,
#                                                     LAG_PRIO_NUM_LEVELS))),
#                   ADD_PRIO(0, OFFLOADS_MIN_LEVEL, 0, FS_CHAINING_CAPS,
#                            ADD_NS(MLX5_FLOW_TABLE_MISS_ACTION_DEF,
#                                   ADD_MULTIPLE_PRIO(OFFLOADS_NUM_PRIOS,
#                                                     OFFLOADS_MAX_FT))),
#                   ADD_PRIO(0, ETHTOOL_MIN_LEVEL, 0, FS_CHAINING_CAPS,
#                            ADD_NS(MLX5_FLOW_TABLE_MISS_ACTION_DEF,
#                                   ADD_MULTIPLE_PRIO(ETHTOOL_NUM_PRIOS,
#                                                     ETHTOOL_PRIO_NUM_LEVELS))),
#                   ADD_PRIO(0, KERNEL_MIN_LEVEL, 0, {},
#                            ADD_NS(MLX5_FLOW_TABLE_MISS_ACTION_DEF,
#                                   ADD_MULTIPLE_PRIO(KERNEL_NIC_TC_NUM_PRIOS,
#                                                     KERNEL_NIC_TC_NUM_LEVELS),
#                                   ADD_MULTIPLE_PRIO(KERNEL_NIC_NUM_PRIOS,
#                                                     KERNEL_NIC_PRIO_NUM_LEVELS))),
#                   ADD_PRIO(0, BY_PASS_MIN_LEVEL, 0, FS_CHAINING_CAPS,
#                            ADD_NS(MLX5_FLOW_TABLE_MISS_ACTION_DEF,
#                                   ADD_MULTIPLE_PRIO(LEFTOVERS_NUM_PRIOS,
#                                                     LEFTOVERS_NUM_LEVELS))),
#                   ADD_PRIO(0, ANCHOR_MIN_LEVEL, 0, {},
#                            ADD_NS(MLX5_FLOW_TABLE_MISS_ACTION_DEF,
#                                   ADD_MULTIPLE_PRIO(ANCHOR_NUM_PRIOS,
#                                                     ANCHOR_NUM_LEVELS))),
#         }
# };
#
# So we got:
#
# fs_prio ffff9a8778b0ac00, num_level:    9, start_level:   49, prio:    4, num_ft:    0
#         mlx5_flow_namespace ffff9a8778b0ca00
#                 fs_prio ffff9a8778b0d600, num_level:    2, start_level:   49, prio:    0, num_ft:    9
#                         mlx5_flow_table ffff9a8730433400        id: c0003, max_fte:   400000, level:  49, type: (enum fs_flow_table_type)FS_FT_NIC_RX    <= this the chain(0, 1, 0)
#                 fs_prio ffff9a8778b0d000, num_level:    7, start_level:   51, prio:    1, num_ft:    8
#                         mlx5_flow_table ffff9a8762c58400        id: 40005, max_fte:    10000, level:  52, type: (enum fs_flow_table_type)FS_FT_NIC_RX
#                         mlx5_flow_table ffff9a873168cc00        id: 40004, max_fte:    10000, level:  53, type: (enum fs_flow_table_type)FS_FT_NIC_RX
#                         mlx5_flow_table ffff9a8763099c00        id:     2, max_fte:       80, level:  54, type: (enum fs_flow_table_type)FS_FT_NIC_RX
#                         mlx5_flow_table ffff9a876309cc00        id:     1, max_fte:       80, level:  55, type: (enum fs_flow_table_type)FS_FT_NIC_RX
#                         mlx5_flow_table ffff9a8709725800        id: 40000, max_fte:    10000, level:  56, type: (enum fs_flow_table_type)FS_FT_NIC_RX
#                         mlx5_flow_table ffff9a8731dde400        id: 40001, max_fte:    10000, level:  56, type: (enum fs_flow_table_type)FS_FT_NIC_RX
#                         mlx5_flow_table ffff9a8749049000        id: 40002, max_fte:    10000, level:  56, type: (enum fs_flow_table_type)FS_FT_NIC_RX
#                         mlx5_flow_table ffff9a8749044c00        id: 40003, max_fte:    10000, level:  56, type: (enum fs_flow_table_type)FS_FT_NIC_RX
