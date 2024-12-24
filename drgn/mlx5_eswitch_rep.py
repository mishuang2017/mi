#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

mlx5e_priv = lib.get_mlx5_pf0()

# struct mlx5_eswitch_rep

mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
print(mlx5e_priv.ppriv)
vports = mlx5_eswitch.offloads.vport_reps
total_vports = mlx5_eswitch.total_vports
enabled_vports = mlx5_eswitch.enabled_vports

print("esw mode: %d" % mlx5_eswitch.mode)
print("total_vports: %d" % total_vports)
print("enabled_vports: %d" % enabled_vports)

# vport_reps = mlx5e_priv.mdev.priv.eswitch.offloads.vport_reps
# for i in range(3):
#     print(vport_reps[i])
# print(vport_reps[total_vports - 1])

i=1
for node in radix_tree_for_each(vports):
    mlx5_eswitch_rep = Object(prog, 'struct mlx5_eswitch_rep', address=node[1].value_())
    if mlx5_eswitch_rep.vport == 0xffff:
        print("=== %d ===" % i)
        print("port: %x" % mlx5_eswitch_rep.vport)
        print(mlx5_eswitch_rep.rep_data[0])
        print(mlx5_eswitch_rep.rep_data[1])
    i=i+1

exit(0)
print("========================== port 2 ================================")
mlx5e_priv = lib.get_mlx5_pf1()
vports = mlx5_eswitch.offloads.vport_reps
i=1
for node in radix_tree_for_each(vports):
    print("=== %d ===" % i)
    i=i+1
    mlx5_eswitch_rep = Object(prog, 'struct mlx5_eswitch_rep', address=node[1].value_())
    if mlx5_eswitch_rep.vport == 0xffff:
        print(mlx5_eswitch_rep)
        print(mlx5_eswitch_rep.rep_data[0])
        print(mlx5_eswitch_rep.rep_data[1])
