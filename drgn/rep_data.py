#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append('.')
from lib import *

# struct mlx5_eswitch_rep

def print_rep_data(mlx5e_priv):
    mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
    print(mlx5e_priv.ppriv)
    if mlx5e_priv.ppriv.value_() == 0:
        return
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
        print("=== %d ===" % i)
        i=i+1
        mlx5_eswitch_rep = Object(prog, 'struct mlx5_eswitch_rep', address=node[1].value_())
        print(mlx5_eswitch_rep)

print("========================= port 1 =====================")
mlx5e_priv = get_mlx5_pf0()
print_rep_data(mlx5e_priv)
print("========================= port 2 =====================")
mlx5e_priv = get_mlx5_pf1()
print_rep_data(mlx5e_priv)

