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

mlx5e_priv = get_mlx5_pf0()

priv = mlx5e_priv.mdev.priv
steering = priv.steering
# print(steering)

print('')
print("FDB_BYPASS_PATH:    %d" % prog['FDB_BYPASS_PATH'])
print("FDB_CRYPTO_INGRESS: %d" % prog['FDB_CRYPTO_INGRESS'])
print("FDB_TC_OFFLOAD:     %d" % prog['FDB_TC_OFFLOAD'])
print("FDB_FT_OFFLOAD:     %d" % prog['FDB_FT_OFFLOAD'])
print("FDB_SLOW_PATH:      %d" % prog['FDB_SLOW_PATH'])
print("FDB_CRYPTO_EGRESS:  %d" % prog['FDB_CRYPTO_EGRESS'])
print("FDB_PER_VPORT:      %d" % prog['FDB_PER_VPORT'])

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
        print_prio(prio, 0)
#             ns = list_first_entry(prio_node.children, "struct mlx5_flow_namespace", "node.list")
#             print("\tmlx5_flow_namespace %x" % ns)
#             print_namespace_level2(ns)
#         table_addr = prio.node.children.address_of_()
#         for table_node in list_for_each_entry('struct fs_node', table_addr, 'list'):
#             if table_node.type.value_() == prog['FS_TYPE_NAMESPACE'].value_():
#                 namespace = container_of(table_node, "struct mlx5_flow_namespace", "node")
#                 print_namespace(namespace)
#             elif table_node.type.value_() == prog['FS_TYPE_PRIO'].value_():
#                 print_prio(prio)
#             else:
#                 print(prio)
#                 table = cast("struct mlx5_flow_table *", table_node)
#                 print_table(table)

# offloads = priv.eswitch.fdb_table.offloads
# print(offloads)

root_ns = steering.root_ns
print('')
print("============ root_ns mlx5_flow_namespace %x ===============\n" % root_ns)
print_namespace(root_ns.ns)
print('')
