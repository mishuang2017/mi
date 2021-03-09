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

root_ns = steering.root_ns
print(root_ns.mode)
print("steering.root_ns.root_ft: %lx" % root_ns.root_ft)

def print_prio(prio):
    print("prio:\t", end='')
    num_levels = prio.num_levels.value_()
    start_level = prio.start_level.value_()
    prio1 = prio.prio.value_()
    num_ft = prio.num_ft.value_()
    print("start_level: %4d, num_levels: %4d, prio: %4d, num_ft: %4d" % \
            (start_level, num_levels, prio1, num_ft))

def print_table(table):
    id = table.id
    max_fte = table.max_fte
    level = table.level
    type = table.type
    print("\tmlx5_flow_table %lx" % table)
    print("\t\tid: %5x, max_fte: %3x, level: %3d, type: %x" % \
        (id, max_fte, level, type), end='')
    print(type)

def print_namespace(ns):
    print("mlx5_flow_namespace %lx" % ns.address_of_())
    prio_addr = ns.node.children.address_of_()
    for prio_node in list_for_each_entry('struct fs_node', prio_addr, 'list'):
        prio = cast("struct fs_prio *", prio_node)
#         print("level 1 namespace")
        print_prio(prio)
#         print(prio)

        n2_addr = prio.node.children.address_of_()
        for n2_node in list_for_each_entry('struct fs_node', n2_addr, 'list'):
            n2 = cast("struct mlx5_flow_namespace *", n2_node)
#             print("level 2 prio")
#             print(n2)

            p3_addr = n2.node.children.address_of_()
            for p3_node in list_for_each_entry('struct fs_node', p3_addr, 'list'):
                p3 = cast("struct fs_prio *", p3_node)
#                 print("level 3 prio")
#                 print(p3)

                table_addr = p3.node.children.address_of_()
                for table_node in list_for_each_entry('struct fs_node', table_addr, 'list'):
                    table = cast("struct mlx5_flow_table *", table_node)
#                     print("level 4 flow table")
                    print_table(table)

print_namespace(root_ns.ns)
