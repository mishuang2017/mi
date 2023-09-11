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
mlx5e_priv = get_mlx5e_priv(pf0_name)
fs = mlx5e_priv.fs
print(fs.vlan_strip_disable)
