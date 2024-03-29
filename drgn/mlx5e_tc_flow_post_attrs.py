#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

print_mlx5e_tc_flow_flags()

for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    addr = dev.value_()
    if "enp" not in name:
        continue;

    mlx5e_priv_addr = addr + prog.type('struct net_device').size
    mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)

    ppriv = mlx5e_priv.ppriv
    if ppriv.value_() == 0:
        continue

#     print(name)
#     print(dev.name)
    mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())
    tc_ht = mlx5e_rep_priv.tc_ht

    for i, flow in enumerate(hash(tc_ht, 'struct mlx5e_tc_flow', 'node')):
#         print(flow.attr.esw_attr[0])
        print(" --- %d ---" % (i + 1))
        print_mlx5e_tc_flow(flow)
        print(flow.attrs)
        j = 1
        for mlx5_flow_attr in list_for_each_entry('struct mlx5_flow_attr', flow.attrs.address_of_(), 'list'):
            print(" === %d ===" % j)
            print(mlx5_flow_attr)
            print(mlx5_flow_attr.esw_attr[0])
            j = j + 1
