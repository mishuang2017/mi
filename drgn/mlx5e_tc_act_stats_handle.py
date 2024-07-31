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
mlx5e_priv2 = get_mlx5_pf1()

def print_handle(priv):
    print('----------------------------')
    print(priv.netdev.name)
    mlx5e_rep_priv = get_mlx5e_rep_priv()
    uplink_priv = mlx5e_rep_priv.uplink_priv
    # print(uplink_priv)
    handle = uplink_priv.action_stats_handle
    # print(handle)

    for i, stat in enumerate(hash(handle.ht, 'struct mlx5e_tc_act_stats', 'hash')):
    #     print("tc_act_cookie: %x" % stat.tc_act_cookie, end='\t')
    #     print(stat.key.peer)
    #     print(stat.peer)
        print("tc_act %x" % stat.tc_act_cookie, end='\t')
        a = cast("struct tc_action *", stat.tc_act_cookie)
        print("%20s" % a.ops.kind.string_().decode(), end='\t')
    #     print("packets: %ld" % stat.lastpackets)
        print("%d" % stat.refcnt.refs.counter)

print_handle(mlx5e_priv)
print_handle(mlx5e_priv2)

