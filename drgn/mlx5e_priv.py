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
# print(mlx5e_priv)
rx_res = mlx5e_priv.rx_res
print(rx_res)

for i in range(16):
    print(rx_res.rss[i])

num = mlx5e_priv.channels.params.num_channels
print(num)
