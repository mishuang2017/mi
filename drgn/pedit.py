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
offloads = mlx5e_priv.mdev.priv.eswitch.offloads

# ofed 4.6
# mod_hdr_tbl = offloads.mod_hdr_tbl

# ofed 4.7
# mod_hdr_tbl = offloads.mod_hdr.hlist

try:
    prog.type('struct mod_hdr_tbl')
    mod_hdr_tbl = offloads.mod_hdr.hlist
except LookupError as x:
    mod_hdr_tbl = offloads.mod_hdr_tbl

for i in range(256):
    node = mod_hdr_tbl[i].first
    while node.value_():
        obj = container_of(node, "struct mlx5e_mod_hdr_handle", "mod_hdr_hlist")
        mlx5e_mod_hdr_handle = Object(prog, 'struct mlx5e_mod_hdr_handle', address=obj.value_())
        # old ofed
#         print("mlx5e_mod_hdr_handle %lx, mod_hdr_id %lx" % (obj.value_(), mlx5e_mod_hdr_handle.mod_hdr_id.value_()))
        # ofed 5.0
#         print(mlx5e_mod_hdr_handle)
        print("mlx5e_mod_hdr_handle %lx, mod_hdr_id 0x%lx refcnt: %d" % \
            (obj.value_(), mlx5e_mod_hdr_handle.modify_hdr.id.value_(), mlx5e_mod_hdr_handle.refcnt.refs.counter))

        print("modify_hdr id: %x" % mlx5e_mod_hdr_handle.modify_hdr.id)
        print_mod_hdr_key(mlx5e_mod_hdr_handle.key)

        node = node.next
