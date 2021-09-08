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
mlx5_vxlan = mlx5e_priv.mdev.vxlan
# print(mlx5_vxlan)

hashtbl = mlx5_vxlan.htable

for i in range(16):
    node = hashtbl[i].first
    while node.value_():
        obj = container_of(node, "struct mlx5_vxlan_port", "hlist")
        mlx5_vxlan_port = Object(prog, 'struct mlx5_vxlan_port', address=obj.value_())
        print(mlx5_vxlan_port)
        node = node.next


