#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

sys.path.append(".")
from lib import *

# mlx5e_priv = get_mlx5_pf0()
# struct mlx5_esw_offload
# offloads = mlx5e_priv.mdev.priv.eswitch.offloads
# encap_tbl = offloads.encap_tbl
# for i in range(256):
#     node = encap_tbl[i].first
#     while node.value_():
#         mlx5e_encap_entry = container_of(node, "struct mlx5e_encap_entry", "encap_hlist")
#         print_mlx5e_encap_entry(mlx5e_encap_entry)
#         node = node.next

mlx5e_rep_priv = get_mlx5e_rep_priv()
addr = mlx5e_rep_priv.neigh_update.neigh_list.address_of_()
i=1
for nhe in list_for_each_entry('struct mlx5e_neigh_hash_entry', addr, 'neigh_list'):
    print("================================= mlx5e_neigh_hash_entry ================================")
#     print(nhe)
    print("mlx5e_neigh_hash_entry %lx" % nhe.value_())
    print("nhe %d" % i);
    i = i + 1
#     continue
    j=1
    for e in list_for_each_entry('struct mlx5e_encap_entry', nhe.encap_list.address_of_(), 'encap_list'):
        print("\t===================== mlx5e_encap_entry =========================")
        print_mlx5e_encap_entry(e)
#         print(e.flows)
        print("\tmlx5e_encap_entry %lx, refcnt: %d, pkt_reformat: %x" %
            (e.value_(), e.refcnt.refs.counter, e.pkt_reformat))
#         if e.pkt_reformat:
#             print("\tencap reformat id: %x" % e.pkt_reformat.action.dr_action.reformat.id)
        print("\tencap %d" % j);
        j=j+1
#         continue

#         print(e.flows)
        k=1
        for item in list_for_each_entry('struct encap_flow_item', e.flows.address_of_(), 'list'):
            print("\tmlx5e_tc_flow %d" % k);
            k=k+1
#             print(item)
            size = prog.type('struct encap_flow_item').size
#             print(item.index)
            flow = container_of(item + size * item.index, "struct mlx5e_tc_flow", "encaps")
            print_mlx5e_tc_flow(flow)
            print_completion(flow.init_done)
