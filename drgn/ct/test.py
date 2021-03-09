#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

import sys
import os

sys.path.append("..")
from lib import *

def print_xarray(x):
    print("flags: %x" % x.xa_flags)
    print("xa_head: %x" % x.xa_head)

for node in radix_tree_for_each(fte_ids.idr_rt):
    mlx5_ct_flow = Object(prog, 'struct mlx5_ct_flow', address=node[1].value_())
