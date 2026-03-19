#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
import time
import sys
import os

# xarray

# print esw->vports, struct mlx5_vport

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

mlx5e_priv = lib.get_mlx5_pf0()
mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
page_root_xa = mlx5e_priv.mdev.priv.page_root_xa

for node in radix_tree_for_each(page_root_xa.address_of_()):
    rb_root = Object(prog, 'struct rb_root', address=node[1].value_())
    for node2 in rbtree_inorder_for_each(rb_root):
        print(node2)
        fw_page = container_of(node2, "struct fw_page", "rb_node")
        print(fw_page)
