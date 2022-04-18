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
esw = mlx5e_priv.mdev.priv.eswitch
# print(mlx5e_priv.mdev.priv.eswitch)
print("mode: %d" % esw.mode)
print(esw.user_count)
print(mlx5e_priv.ppriv)

print(esw.offloads.rep_ops[0])

print(esw.unload_reps_lock)
