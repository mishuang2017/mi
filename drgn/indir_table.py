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
indir = mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.indir
# print(indir)

table = indir.table

for i in range(256):
    node = table[i].first
    while node.value_():
        obj = container_of(node, "struct mlx5_esw_indir_table_entry", "hlist")
#         obj = container_of(node, "struct esw_indir_tbl_entry", "hlist")
#         print(obj)
        vport = obj.vport
        print(" ======== vport: %d =========" % vport)
        ft = obj.ft
        flow_table("", ft)
        node = node.next
