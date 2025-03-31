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
# print(dev.dm)

priv = dev.priv
steering = priv.steering
print("esw->dev->priv.steering->mode: ", end='')
print(steering.mode)

root_ns = steering.fdb_root_ns.ns
mlx5_flow_root_namespace = Object(prog, 'struct mlx5_flow_root_namespace', address=root_ns.address_of_())
# print(root_ns)
fs_dr_domain = mlx5_flow_root_namespace.fs_dr_domain
# print(fs_dr_domain.dr_domain.refcount)
print(fs_dr_domain.dr_domain.type)
print(fs_dr_domain.dr_domain.refcount)

# print(fs_dr_domain)

mlx5dr_domain = fs_dr_domain.dr_domain
# print(mlx5dr_domain)

mlx5dr_icm_pool = mlx5dr_domain.ste_icm_pool
# print(mlx5dr_icm_pool)

mlx5dr_ste_ctx = mlx5dr_domain.ste_ctx
# print(mlx5dr_ste_ctx)

def print_mlx5dr_table(dr):
    print("======= start =======\n")
    print("mlx5dr_table %x" % dr)
    for matcher in list_for_each_entry('struct mlx5dr_matcher', dr.matcher_list.address_of_(), 'list_node'):
        print("mlx5dr_matcher %x" % matcher)
        print(matcher.dbg_rule_list)
        for rule in list_for_each_entry('struct mlx5dr_rule', matcher.dbg_rule_list.address_of_(), 'dbg_node'):
            print(rule)
            # print(rule.tx.last_rule_ste)
    print("======= end =======\n")

i = 1
# ofed
# for tbl in list_for_each_entry('struct mlx5dr_table', mlx5dr_domain.tbl_list.address_of_(), 'list_node'):
# upstream
for tbl in list_for_each_entry('struct mlx5dr_table', mlx5dr_domain.dbg_tbl_list.address_of_(), 'dbg_node'):
    print("%3d: mlx5dr_table %x, id: %4d, %#x" % (i, tbl, tbl.table_id, tbl.table_id))
    i = i + 1
    if tbl.table_id == 0xb:
       print_mlx5dr_table(tbl)
#        print(tbl.tx)
