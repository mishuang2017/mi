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
mlx5e_rep_priv = get_mlx5e_rep_priv()
uplink_priv = mlx5e_rep_priv.uplink_priv
# print(uplink_priv)
handle = uplink_priv.action_stats_handle
# print(handle)

for i, stat in enumerate(hash(handle.ht, 'struct mlx5e_tc_act_stats', 'hash')):
    print("tc_act_cookie: %x" % stat.tc_act_cookie, end='\t')
#     print(stat)
    print("packets: %ld" % stat.lastpackets)
