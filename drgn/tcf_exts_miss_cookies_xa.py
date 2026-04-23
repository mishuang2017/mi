#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

# xarray

# print esw->vports, struct mlx5_vport

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

tcf_exts_miss_cookies_xa = prog['tcf_exts_miss_cookies_xa']
# print(tcf_exts_miss_cookies_xa)

for node in radix_tree_for_each(tcf_exts_miss_cookies_xa.address_of_()):
    node = Object(prog, 'struct tcf_exts_miss_cookie_node', address=node[1].value_())
    print(node)
