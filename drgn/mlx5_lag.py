#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5e_priv(pf0_name)
mlx5_lag = mlx5e_priv.mdev.priv.lag
print("flags: %x" % mlx5_lag.flags)

MLX5_LAG_FLAG_ROCE = prog['MLX5_LAG_FLAG_ROCE']
MLX5_LAG_FLAG_SRIOV = prog['MLX5_LAG_FLAG_SRIOV']
MLX5_LAG_FLAG_MULTIPATH = prog['MLX5_LAG_FLAG_MULTIPATH']
MLX5_LAG_FLAG_READY = prog['MLX5_LAG_FLAG_READY']

print("MLX5_LAG_FLAG_ROCE: %x" % MLX5_LAG_FLAG_ROCE)
print("MLX5_LAG_FLAG_SRIOV: %x" % MLX5_LAG_FLAG_SRIOV)
print("MLX5_LAG_FLAG_MULTIPATH: %x" % MLX5_LAG_FLAG_MULTIPATH)
print("MLX5_LAG_FLAG_READY: %x" % MLX5_LAG_FLAG_READY)
