#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import socket
import sys
import os

sys.path.append(".")
from lib_pedit import *


# struct mlx5_esw_offload

def print_table(priv):
    print("%x" % priv)
    table = priv.mdev.priv.eswitch.fdb_table.offloads.indir.table
    for i in range(256):
        node = table[i].first
    #     print(node)
        while node.value_():
            obj = container_of(node, "struct mlx5_esw_indir_table_entry", "hlist")
            vport = obj.vport
            print("--- vport: %d ---" % vport)
            ft = obj.ft
            flow_table("", ft)
            node = node.next

    #         print(obj)

dev = netdev_get_by_name(prog['init_net'], "enp8s0f0")
mlx5e_priv = get_mlx5(dev)
# mlx5e_priv = get_mlx5_pf0()
print("=== indir_table p0 ===")
print_table(mlx5e_priv)

dev = netdev_get_by_name(prog['init_net'], "enp8s0f1")
mlx5e_priv = get_mlx5(dev)
# mlx5e_priv = get_mlx5_pf1()
print("=== indir_table p1 ===")
print_table(mlx5e_priv)
