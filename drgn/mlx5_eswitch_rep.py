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
vports = mlx5_eswitch.vports
total_vports = mlx5_eswitch.total_vports
enabled_vports = mlx5_eswitch.enabled_vports

print("esw mode: %d" % mlx5_eswitch.mode)
print("total_vports: %d" % total_vports)
print("enabled_vports: %d" % enabled_vports)

vport_reps = mlx5e_priv.mdev.priv.eswitch.offloads.vport_reps
for i in range(3):
    print(vport_reps[i])

print(vport_reps[total_vports - 1])
