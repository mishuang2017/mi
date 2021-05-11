#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

mlx5e_priv = get_mlx5_pf0()

# struct mlx5_esw_offload
offloads = mlx5e_priv.mdev.priv.eswitch.offloads

termtbl_tbl = offloads.termtbl_tbl

for i in range(256):
    node = termtbl_tbl[i].first
    while node.value_():
        obj = container_of(node, "struct mlx5_termtbl_handle", "termtbl_hlist")
        print("mlx5_termtbl_handle %lx" % obj.value_())
        mlx5_termtbl_handle = Object(prog, 'struct mlx5_termtbl_handle', address=obj.value_())
        print(mlx5_termtbl_handle)
        termtbl = mlx5_termtbl_handle.termtbl
        flow_table("termtbl", termtbl)
        node = node.next
