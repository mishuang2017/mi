#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

sys.path.append(".")
from lib import *

# mlx5e_priv = get_mlx5_pf0()
# struct mlx5_esw_offload
# offloads = mlx5e_priv.mdev.priv.eswitch.offloads
# encap_tbl = offloads.encap_tbl
# for i in range(256):
#     node = encap_tbl[i].first
#     while node.value_():
#         mlx5e_encap_entry = container_of(node, "struct mlx5e_encap_entry", "encap_hlist")
#         print_mlx5e_encap_entry(mlx5e_encap_entry)
#         node = node.next

mlx5e_rep_priv = get_mlx5e_rep_priv()
addr = mlx6e_rep_priv.neigh_update.neigh_list.address_of_()
for nhe in list_for_each_entry('struct mlx5e_neigh_hash_entry', addr, 'neigh_list'):
    print(nhe)
#     print("mlx5e_neigh_hash_entry %lx" % nhe.value_())
    for e in list_for_each_entry('struct mlx5e_encap_entry', nhe.encap_list.address_of_(), 'encap_list'):
        print(e)
#         print_mlx5e_encap_entry(e)
