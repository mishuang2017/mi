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
udp_tunnel_nic = mlx5e_priv.netdev.udp_tunnel_nic

for i in range(udp_tunnel_nic.n_tables):
    print(udp_tunnel_nic.entries[i])
    print("port: %d" % ntohs(udp_tunnel_nic.entries[i].port))
