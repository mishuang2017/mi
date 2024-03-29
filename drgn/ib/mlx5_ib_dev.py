#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append("..")
from lib import *

mlx5e_priv = get_mlx5_pf0()

# struct mlx5_eswitch_rep

mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
# print(mlx5e_priv.ppriv)
vports = mlx5_eswitch.offloads.vport_reps
total_vports = mlx5_eswitch.total_vports
enabled_vports = mlx5_eswitch.enabled_vports

# print("esw mode: %d" % mlx5_eswitch.mode)
print("total_vports: %d" % total_vports)
print("enabled_vports: %d" % enabled_vports)

# vport_reps = mlx5e_priv.mdev.priv.eswitch.offloads.vport_reps
# for i in range(3):
#     print(vport_reps[i])
# print(vport_reps[total_vports - 1])

i=1
for node in radix_tree_for_each(vports):
    mlx5_eswitch_rep = Object(prog, 'struct mlx5_eswitch_rep', address=node[1].value_())
    priv = mlx5_eswitch_rep.rep_data[1].priv
    if priv:
        print("\n=== %d ===" % i)
        print("mlx5_eswitch_rep %x" % node[1].value_())
        print("mlx5_ib_dev %x" % priv)
        mlx5_ib_dev = Object(prog, 'struct mlx5_ib_dev', address=priv)
        print(mlx5_ib_dev.num_ports)
        print(mlx5_eswitch_rep.vport)
#         print(mlx5_ib_dev.port.roce)
    i=i+1

# mlx5_ib_dev_list = prog['mlx5_ib_dev_list']
# print(mlx5_ib_dev_list)
# for dev in list_for_each_entry('struct mlx5_ib_dev', mlx5_ib_dev_list.address_of_(), 'ib_dev_list'):
#     print(dev)
