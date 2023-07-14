#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import socket
import sys
import os

sys.path.append(".")
from lib_pedit import *

mlx5e_priv = get_mlx5_pf0()

# struct mlx5_esw_offload
decap_tbl = mlx5e_priv.mdev.priv.eswitch.offloads.decap_tbl
print(decap_tbl)

# exit(0)

for i in range(256):
    node = decap_tbl[i].first
    while node.value_():
        obj = container_of(node, "struct mlx5e_decap_entry", "hlist")
        print(obj)
        node = node.next
