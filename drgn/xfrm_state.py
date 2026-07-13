#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5e_priv(pf0_name)
ipsec = mlx5e_priv.ipsec
# print(ipsec)
# exit(0)
# print(mlx5e_priv.netdev.xfrmdev_ops)

def print_sadb(sadb):
    for node in radix_tree_for_each(sadb.address_of_()):
        while node.value_():
            obj = container_of(node, "struct mlx5e_ipsec_sa_entry", "hlist")
            sa = Object(prog, 'struct mlx5e_ipsec_sa_entry', address=obj.value_())
            print("sa->attrs->flags, MLX5_ACCEL_ESP_FLAGS_TUNNEL 1, MLX5_ACCEL_ESP_FLAGS_FULL_OFFLOAD 8\n")
            print(sa)
            print(sa.ipsec.aso)
            print(sa.ipsec.aso.maso)
            print(sa.ipsec.aso.umr)
            
            print_mlx5_flow_handle(sa.ipsec_rule.rule)

            node = node.next

sadb = ipsec.sadb
print_sadb(sadb)

def print_net_xfrm_state(net):
    netns_xfrm = net.xfrm

    print("\n======================== net.xfrm.state ===========================\n")

    i=1
    for x in list_for_each_entry('struct xfrm_state', netns_xfrm.state_all.address_of_(), 'km.all'):
        print(" --- %d ---\n" % i)

        print(x.dir)
        print(x.replay)
        print(x.replay_esn)
        i+=1

net = prog['init_net']
print_net_xfrm_state(net)
