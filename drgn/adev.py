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
priv = mlx5e_priv.mdev.priv
print(priv.adev[0])
print(priv.adev[1])
print(priv.adev_idx)


mlx5e_priv = get_mlx5e_priv(pf1_name)
priv = mlx5e_priv.mdev.priv
print(priv.adev_idx)
