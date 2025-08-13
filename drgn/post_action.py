#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_rep_priv = get_mlx5e_rep_priv()
# print(mlx5e_rep_priv.uplink_priv)
post_act = mlx5e_rep_priv.uplink_priv.post_act
# print(post_act)
flow_table("", post_act.ft)

for node in radix_tree_for_each(post_act.ids):
    mlx5_flow_attr = Object(prog, 'struct mlx5_flow_attr', address=node[1].value_())
    print(mlx5_flow_attr.post_act_handle)
