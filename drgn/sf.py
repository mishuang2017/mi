#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

sys.path.append(".")
from lib import *

IFNAME = sys.argv[1] if len(sys.argv) > 1 else pf0_name

def print_mlx5_sf(mlx5_sf_table):
    for node in radix_tree_for_each(mlx5_sf_table.function_ids.address_of_()):
        sf = Object(prog, 'struct mlx5_sf', address=node[1].value_())
        print("port_index: %d, %#x, controller: %d, id: %d, hw_fn_id: %d, %#x hw_state: %d" % \
            (sf.port_index, sf.port_index, sf.controller, sf.id, sf.hw_fn_id, sf.hw_fn_id, sf.hw_state))

mlx5e_priv = get_mlx5e_priv(IFNAME)

print(" === sf rep / mlx5_sf_table.function_ids (%s) === " % IFNAME)
mlx5_sf_table = mlx5e_priv.mdev.priv.sf_table
print_mlx5_sf(mlx5_sf_table)

print("\n === mlx5e_priv.mdev.priv.sf_hw_table (%s) === \n" % IFNAME)
mlx5_sf_hwc_table = mlx5e_priv.mdev.priv.sf_hw_table
# print(mlx5_sf_hwc_table)

print("\n === mlx5e_priv.mdev.priv.esw_n_head (%s) === \n" % IFNAME)
n_head = mlx5e_priv.mdev.priv.esw_n_head
notifier_block = n_head.head
while True:
    if notifier_block.value_() == 0:
        break
    print(notifier_block)
    mlx5_core_dev = container_of(notifier_block, "struct mlx5_core_dev", "priv.sf_table_esw_nb")
    notifier_block = notifier_block.next

print("\n === mlx5e_priv.mdev.priv.vhca_state_n_head (%s) === \n" % IFNAME)
n_head = mlx5e_priv.mdev.priv.vhca_state_n_head
notifier_block = n_head.head
i = 1
while True:
    if notifier_block.value_() == 0:
        break
    print("---%d---" % i)
    print(notifier_block)
    mlx5_core_dev = container_of(notifier_block, "struct mlx5_core_dev", "priv.sf_table_esw_nb")
    notifier_block = notifier_block.next
    i = i + 1

print("\n === sf devs (%s) === \n" % IFNAME)
mlx5_sf_dev_table = mlx5e_priv.mdev.priv.sf_dev_table
if mlx5_sf_dev_table:
    for node in radix_tree_for_each(mlx5_sf_dev_table.devices.address_of_()):
        mlx5_sf_dev = Object(prog, 'struct mlx5_sf_dev', address=node[1].value_())
        print(mlx5_sf_dev.adev.dev.kobj.name.string_().decode())
        print("mlx5_sf_dev.sfnum: %d" % mlx5_sf_dev.sfnum)
