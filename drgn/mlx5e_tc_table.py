#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

mlx5e_priv = get_mlx5_pf0()
# print(mlx5e_priv)
mlx5e_tc_table = mlx5e_priv.fs.tc
# print(mlx5e_tc_table.chains)
# print(mlx5e_tc_table.chains.dev.priv.eswitch)
# print(mlx5e_tc_table.netdevice_nb)
# print(mlx5e_tc_table.netdevice_nn)

mlx5e_l2_table = mlx5e_priv.fs.l2
# print(mlx5e_l2_table)
flow_table("l2", mlx5e_l2_table.ft.t)
print("\n===mlx5e_l2_table.broadcast.rule===\n")
print_mlx5_flow_handle(mlx5e_l2_table.broadcast.rule)
print("\n===mlx5e_l2_table.allmulti.rule===\n")
print_mlx5_flow_handle(mlx5e_l2_table.allmulti.rule)

if mlx5e_priv.fs.promisc.ft.t:
    print("=== mlx5e_priv.fs.promisc.ft.t ===")
    flow_table("mlx5e_priv.fs.promisc.ft.t", mlx5e_priv.fs.promisc.ft.t)
# print("%x:%x:%x:%x:%x:%x:%x:%x" % (a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]))

hairpin_tbl = mlx5e_tc_table.hairpin_tbl
# print(hairpin_tbl)

exit(0)

for i in range(1<<16):
    node = hairpin_tbl[i].first
    while node.value_():
        obj = container_of(node, "struct mlx5e_hairpin_entry", "hairpin_hlist")
        print("mlx5e_hairpin_entry %lx" % obj.value_())
        mlx5e_hairpin_entry = Object(prog, "struct mlx5e_hairpin_entry", address=obj.value_())
        entry = mlx5e_hairpin_entry
        print(mlx5e_hairpin_entry)
        node = node.next

print(entry.hp)
print(entry.hp.pair)
