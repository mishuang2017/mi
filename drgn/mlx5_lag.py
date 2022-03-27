#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

for name in pf0_name, pf1_name:
    mlx5e_priv = get_mlx5e_priv(name)
    print("mlx5e_priv %x" % mlx5e_priv.address_of_().value_())
    mlx5_lag = mlx5e_priv.mdev.priv.lag
    print("mlx5_lag %x" % mlx5_lag)
    print_fib_info(mlx5_lag.lag_mp.mfi)

MLX5_LAG_FLAG_ROCE = prog['MLX5_LAG_FLAG_ROCE']
MLX5_LAG_FLAG_SRIOV = prog['MLX5_LAG_FLAG_SRIOV']
MLX5_LAG_FLAG_MULTIPATH = prog['MLX5_LAG_FLAG_MULTIPATH']
MLX5_LAG_FLAG_READY = prog['MLX5_LAG_FLAG_READY']

print("MLX5_LAG_FLAG_ROCE: %x" % MLX5_LAG_FLAG_ROCE)
print("MLX5_LAG_FLAG_SRIOV: %x" % MLX5_LAG_FLAG_SRIOV)
print("MLX5_LAG_FLAG_MULTIPATH: %x" % MLX5_LAG_FLAG_MULTIPATH)
print("MLX5_LAG_FLAG_READY: %x" % MLX5_LAG_FLAG_READY)
