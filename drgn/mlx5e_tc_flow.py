#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

mlx5e_rep_priv = get_mlx5e_rep_priv()
print(mlx5e_rep_priv)

# if kernel("4.20.16+"):
#     tc_ht = mlx5e_rep_priv.uplink_priv.tc_ht
# else:
#     tc_ht = mlx5e_rep_priv.tc_ht

try:
    prog.type('struct mlx5_rep_uplink_priv')
    tc_ht = mlx5e_rep_priv.uplink_priv.tc_ht
except LookupError as x:
    tc_ht = mlx5e_rep_priv.tc_ht

# hash(tc_ht, 'struct mlx5e_tc_flow', 'node')

# sys.exit(0)

print_mlx5e_tc_flow_flags()
for i, flow in enumerate(hash(tc_ht, 'struct mlx5e_tc_flow', 'node')):
    print_mlx5e_tc_flow(flow)
