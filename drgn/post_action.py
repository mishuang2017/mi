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
post_action = mlx5e_rep_priv.uplink_priv.post_action
# print(post_action)
flow_table("", post_action.ft)

# for node in radix_tree_for_each(post_action.ids):
#     print(node)
#     mlx5_flow_attr = Object(prog, 'struct mlx5_flow_attr', address=node[1].value_())
