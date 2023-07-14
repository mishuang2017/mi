#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import socket
import sys
import os

sys.path.append("..")
from lib_pedit import *

mlx5e_priv = get_mlx5_pf0()

# struct mlx5_esw_offload
offloads = mlx5e_priv.mdev.priv.eswitch.offloads
mod_hdr_tbl = offloads.mod_hdr_tbl

for i in range(256):
    node = mod_hdr_tbl[i].first
    while node.value_():
        mlx5e_mod_hdr_entry = container_of(node, "struct mlx5e_mod_hdr_entry", "mod_hdr_hlist")
        print(mlx5e_mod_hdr_entry.key)
        print_mod_hdr_key(mlx5e_mod_hdr_entry.key)
        node = node.next
