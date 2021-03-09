#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

mlx5e_priv = lib.get_mlx5_pf0()
mlx5e_rep_priv = mlx5e_priv.ppriv

def print_neigh_hash_entry(n):
    print(n)
#     print("mlx5e_neigh.dst_ip: %s" % n.m_neigh.dst_ip.v6.in6_u.u6_addr8)

def print_encap(e):
    print(e)
#     print("encap_id: %d" % e.encap_id)

mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=mlx5e_rep_priv.value_())
encap_list = mlx5e_rep_priv.neigh_update.neigh_list.address_of_()
for neigh_hash in list_for_each_entry('struct mlx5e_neigh_hash_entry', encap_list, 'neigh_list'):
    print_neigh_hash_entry(neigh_hash)
    encap_list2 = neigh_hash.encap_list.address_of_()
    for encap in list_for_each_entry('struct mlx5e_encap_entry', encap_list2, 'encap_list'):
        print_encap(encap)
        flows = encap.flows.address_of_()
        for flow in list_for_each_entry('struct mlx5e_tc_flow', flows, 'encaps[0].list'):
            print(flow.priv.netdev.name.string_().decode())
