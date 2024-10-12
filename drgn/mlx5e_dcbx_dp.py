#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

print("===================== port 1 =======================")
print(pf0_name)
mlx5e_priv = get_mlx5e_priv(pf0_name)
print(mlx5e_priv.dcbx_dp)
print(mlx5e_priv.selq.active)
