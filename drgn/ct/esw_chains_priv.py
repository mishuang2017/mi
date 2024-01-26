#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import reinterpret
import time
import socket

import sys
import os

sys.path.append("..")
from lib import *

# mlx5e_priv = get_mlx5_pf0()
mlx5e_priv = get_mlx5e_priv(pf0_name)
offloads = mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads
# print(offloads)
slow_fdb = offloads.slow_fdb
esw_chains_priv = offloads.esw_chains_priv

chains_ht =   esw_chains_priv.chains_ht
prios_ht =    esw_chains_priv.prios_ht
mapping_ctx = esw_chains_priv.chains_mapping
# tc_end_ft =  esw_chains_priv.tc_end_ft # net/mlx5: fs_chains: Refactor to detach chains from tc usage
# tc_end_ft =  esw_chains_priv.chains_end_ft

# print("tc_end_ft %lx, slow_fdb: %lx" % (tc_end_ft, slow_fdb))
# print(esw_chains_priv)

for i, chain in enumerate(hash(chains_ht, 'struct fs_chain', 'node')):
#     print(chain)
    print("chain id: %x\nfdb_chain %x" % (chain.id, chain))
#     print("fs_base_prio: %x: fs_base_level %x" % (chain.chains.fs_base_prio, chain.chains.fs_base_level))
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

MLX5_MAPPED_OBJ_CHAIN = prog['MLX5_MAPPED_OBJ_CHAIN']
MLX5_MAPPED_OBJ_ACT_MISS = prog['MLX5_MAPPED_OBJ_ACT_MISS']

def print_chain_mapping(item):
    print("mapping_item %lx" % item, end='\t')
    print("cnt: %d" % item.cnt, end='\t')
    print("id: %d" % item.id, end='\t')
    data = Object(prog, 'struct mlx5_mapped_obj', address=item.data.address_of_())
    if data.type == MLX5_MAPPED_OBJ_CHAIN.value_():
        print("chain:           %d " % data.chain)
    elif data.type == MLX5_MAPPED_OBJ_ACT_MISS.value_():
        print("act_miss_cookie: %d " % data.act_miss_cookie)

print('\n=== chain mapping_ctx ===\n')
ht = mapping_ctx.ht
print("mapping_ctx %lx" % mapping_ctx)
for i in range(256):
    for item in hlist_for_each_entry('struct mapping_item', ht[i], 'node'):
        print_chain_mapping(item)

print('\n=== prios_ht ===')

for i, prio in enumerate(hash(prios_ht, 'struct prio', 'node')):
    key = prio.key
    print("%3d: chain: %8x, prio: %4x, level: %4x" % (i, key.chain, key.prio, key.level))


ft_offloads_restore = mlx5e_priv.mdev.priv.eswitch.offloads.ft_offloads_restore
print("\n=== mlx5e_priv.mdev.priv.eswitch.offloads.ft_offloads_restore ===")
flow_table("", ft_offloads_restore)

print("\n=== split vport table ===\n")
vports = offloads.vports.table
# print(vports)

for i in range(256):
    node = vports[i].first
    while node.value_():
        obj = container_of(node, "struct mlx5_vport_table", "hlist")
        mlx5_vport_table = Object(prog, 'struct mlx5_vport_table', address=obj.value_())
        print(mlx5_vport_table)
        node = node.next

        flow_table("", mlx5_vport_table.fdb)
        print('-----------------------------')

# print("\n=== indir vport table ===\n")
# vports = offloads.indir.table
# print(vports)
# 
# for i in range(256):
#     node = vports[i].first
#     while node.value_():
#         obj = container_of(node, "struct mlx5_vport_table", "hlist")
#         mlx5_vport_table = Object(prog, 'struct mlx5_vport_table', address=obj.value_())
#         print(mlx5_vport_table)
#         node = node.next
# 
#         flow_table("", mlx5_vport_table.fdb)
#         print('-----------------------------')
# 
