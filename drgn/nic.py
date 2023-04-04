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
    if name != "eth4":
        continue;
    print(name)

    mlx5e_priv_addr = addr + prog.type('struct net_device').size
    mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)

    print(name)
    print(dev.name)
    tc_ht = mlx5e_priv.fs.tc.ht

    for i, flow in enumerate(hash(tc_ht, 'struct mlx5e_tc_flow', 'node')):
#         print(flow.attr.esw_attr[0])
        print(" --- %d ---" % (i + 1))
        print_mlx5e_tc_flow(flow)
#         print(flow.attrs)
#         for mlx5_flow_attr in list_for_each_entry('struct mlx5_flow_attr', flow.attrs.address_of_(), 'list'):
#             print(mlx5_flow_attr)
#             print(mlx5_flow_attr.esw_attr[0])


    ct = mlx5e_priv.fs.tc.ct.ct
    flow_table("ct", ct)
    ct_nat = mlx5e_priv.fs.tc.ct.ct_nat
    flow_table("ct_nat", ct_nat)

    post_act = mlx5e_priv.fs.tc.post_act
    # print(post_act)
    flow_table("post_act", post_act.ft)


    chains_ht =   mlx5e_priv.fs.tc.chains.chains_ht
    prios_ht =    mlx5e_priv.fs.tc.chains.prios_ht

    for i, chain in enumerate(hash(chains_ht, 'struct fs_chain', 'node')):
    #     print(chain)
        print("chain id: %x\nfdb_chain %x" % (chain.id, chain))
        for prio in list_for_each_entry('struct prio', chain.prios_list.address_of_(), 'list'):
            fdb = prio.ft
            next_fdb = prio.next_ft
            miss_group = prio.miss_group
            miss_rule = prio.miss_rule
            print("\n=== chain: %x, prio: %x, level: %x ===" % \
                (prio.key.chain, prio.key.prio, prio.key.level))
            print("prio %lx, ref: %d" % (prio, prio.ref))
            print("next_fdb: %lx, miss_group: %lx, miss_rule: mlx5_flow_handle %lx" % \
                (next_fdb, miss_group, miss_rule))
            table = prio.ft
            flow_table("", table)


