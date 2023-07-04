#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

print_mlx5e_tc_flow_flags()

j=1
for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    addr = dev.value_()
    if "enp" not in name and "p0" not in name:
        continue;

    mlx5e_priv_addr = addr + prog.type('struct net_device').size
    mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)

    ppriv = mlx5e_priv.ppriv
    if ppriv.value_() == 0:
        continue

    print('')
    mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())
    tc_ht = mlx5e_rep_priv.tc_ht

    for i, flow in enumerate(hash(tc_ht, 'struct mlx5e_tc_flow', 'node')):
#         print(flow.attr.esw_attr[0])
        print("============================== %d =========================" % j)
        print_mlx5e_tc_flow(flow)
        print(flow.attr.esw_attr[0])
        j=j+1
#         print(flow.attrs)
        k=1
        for mlx5_flow_attr in list_for_each_entry('struct mlx5_flow_attr', flow.attrs.address_of_(), 'list'):
            print("--- flow.attrs: %d ---" % k)
            k=k+1
            print("mlx5_flow_attr.action: %x" % mlx5_flow_attr.action)
            print("flow.attr.tc_act_cookies_count: %d" % mlx5_flow_attr.tc_act_cookies_count)
            for m in range(mlx5_flow_attr.tc_act_cookies_count):
                print("tc_act_cookies[%d]: %x" % (m, mlx5_flow_attr.tc_act_cookies[m]))
#             print(mlx5_flow_attr)
#             print("flow.attr: %x" % mlx5_flow_attr)
#             print(mlx5_flow_attr.post_act_handle)
#             print(mlx5_flow_attr.parse_attr)
#             print(mlx5_flow_attr.esw_attr[0])
