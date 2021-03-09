#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object
from drgn import cast
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

dev = lib.get_mlx5_core_dev(0)
print(dev.coredev_type)

priv = dev.priv
steering = priv.steering
# print(steering)

fdb_root_ns = steering.fdb_root_ns
print(fdb_root_ns.mode)
print("root ft: %lx" % fdb_root_ns.root_ft)


print('')
print("FDB_BYPASS_PATH: %d" % prog['FDB_BYPASS_PATH'])
print("FDB_TC_OFFLOAD:  %d" % prog['FDB_TC_OFFLOAD'])
print("FDB_FT_OFFLOAD:  %d" % prog['FDB_FT_OFFLOAD'])
print("FDB_SLOW_PATH:   %d" % prog['FDB_SLOW_PATH'])
print("FDB_PER_VPORT:   %d" % prog['FDB_PER_VPORT'])

def print_prio(prio):
    num_levels = prio.num_levels.value_()
    start_level = prio.start_level.value_()
    prio1 = prio.prio.value_()
    num_ft = prio.num_ft.value_()
#     print("fs_prio %lx" % prio)
    if num_ft:
        print("prio: num_level: %4d, start_level: %4d, prio: %4d, num_ft: %4d" % \
            (num_levels, start_level, prio1, num_ft))

def print_table(table):
    id = table.id
    max_fte = table.max_fte
    level = table.level
    type = table.type
    print("\tmlx5_flow_table %lx" % table, end='\t')
    print("id: %5x, max_fte: %8x, level: %3d, type: " % \
        (id, max_fte, level), end='')
    print(type)

def print_namespace(ns):
#     print(ns)
    prio_addr = ns.node.children.address_of_()
    for prio_node in list_for_each_entry('struct fs_node', prio_addr, 'list'):
        prio = cast("struct fs_prio *", prio_node)
        print_prio(prio)

        table_addr = prio.node.children.address_of_()
        for table_node in list_for_each_entry('struct fs_node', table_addr, 'list'):
#             print(table_node.type)
            if table_node.type.value_() == prog['FS_TYPE_NAMESPACE'].value_():
                namespace = container_of(table_node, "struct mlx5_flow_namespace", "node")
#                 print(namespace)
#                 print("FS_TYPE_NAMESPACE")
                print_namespace(namespace)
            else:
                table = cast("struct mlx5_flow_table *", table_node)
                print_table(table)

# offloads = priv.eswitch.fdb_table.offloads
# print(offloads)

root_ns = steering.root_ns
print('')
print("============ root_ns ===============")
print_namespace(root_ns.ns)
print('')

print("============ fdb_root_ns ===============")
print_namespace(fdb_root_ns.ns)
print('')

print("============ fdb_sub_ns ===============")
fdb_sub_ns = steering.fdb_sub_ns
for i in range(4):
    ns = fdb_sub_ns[i]

    print("=== namespace %d ===" %i)
    print_namespace(ns)
    print("")
