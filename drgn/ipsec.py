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
print(ipsec)
# exit(0)
print(mlx5e_priv.netdev.xfrmdev_ops)

sadb = ipsec.sadb
print("\n======================== sadb ===========================\n")
# print(sadb)

# crypto
# flow_table("sa", ipsec.tx.ft.sa)
# flow_table("sa", ipsec.tx.ft.pol)

for node in radix_tree_for_each(sadb.address_of_()):
    print(node)
    entry = Object(prog, 'struct mlx5e_ipsec_sa_entry', address=node[1].value_())
    print(entry)

# exit(0)

def print_net_xfrm_state(net):
    netns_xfrm = net.xfrm

    print("\n======================== net.xfrm.state ===========================\n")

    i=1
    for x in list_for_each_entry('struct xfrm_state', netns_xfrm.state_all.address_of_(), 'km.all'):
        print(" --- %d ---\n" % i)
#         print(x)
        print(x.id)
        print("x.xso.flags: XFRM_OFFLOAD_IPV6 1, XFRM_OFFLOAD_INBOUND 2, XFRM_OFFLOAD_FULL, 4")
#         print(x.xso)
        i+=1

def print_net_xfrm_policy(net):
    netns_xfrm = net.xfrm

    print("\n======================== net.xfrm.policy ===========================\n")

    i=1
    for x in list_for_each_entry('struct xfrm_policy_walk_entry', netns_xfrm.policy_all.address_of_(), 'all'):
        print(" --- %d ---\n" % i)
#         print(x)
        policy = container_of(x, "struct xfrm_policy", "walk")
        print(policy.xdo)
        i+=1

net = prog['init_net']
print_net_xfrm_state(net)
print_net_xfrm_policy(net)

def print_counters():
    print("\n======================== counters ===========================\n")

    fc = ipsec_priv.decap_rule_counter
    print("decap_rule_counter       id: %x, packets: %d" % (fc.id, fc.cache.packets))
    fc = ipsec_priv.decap_miss_rule_counter
    print("decap_miss_rule_counter  id: %x, packets: %d" % (fc.id, fc.cache.packets))

    fc = ipsec_priv.tx_chk_rule_counter
    print("tx_chk_rule_counter      id: %x, packets: %d" % (fc.id, fc.cache.packets))
    fc = ipsec_priv.tx_chk_drop_rule_counter
    print("tx_chk_drop_rule_counter id: %x, packets: %d" % (fc.id, fc.cache.packets))

# print_counters()
