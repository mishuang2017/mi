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
sample_priv = uplink_priv.esw_psample

tunnel_mapping = mlx5e_rep_priv.uplink_priv.tunnel_mapping

print('\n=== mlx5_esw_psample ===\n')
print("mlx5_esw_psample %x" % sample_priv)
# print(sample_priv)
ct = 1

# sys.exit(0)

# struct mlx5_esw_offload
offloads = mlx5e_priv.mdev.priv.eswitch.offloads

def print_mlx5_sampler(handle):
    print("sampler_id: %d, sample_ratio: %d, sample_table_id: %x, default_table_id: %x, count: %d" % \
            (handle.sampler_id, handle.sample_ratio, handle.sample_table_id, handle.default_table_id, handle.count))

print('\n=== sampler_termtbl ===')

# termtbl_list = prog['termtbl_list'].address_of_()
# print(termtbl_list)
# for handle in list_for_each_entry('struct mlx5_sampler_termtbl_handle', termtbl_list, 'list'):
#     print(handle)

# print(sample_priv.termtbl)
flow_table("sampler_termtbl", sample_priv.termtbl)

print('\n=== hashtbl ===\n')

hashtbl = sample_priv.hashtbl

for i in range(256):
    node = hashtbl[i].first
    while node.value_():
        obj = container_of(node, "struct mlx5_sampler", "hlist")
#         print("mlx5_sampler %lx" % obj.value_())
        mlx5_sampler = Object(prog, 'struct mlx5_sampler', address=obj.value_())
        print_mlx5_sampler(mlx5_sampler)
        node = node.next

print('\n=== offloads.num_flows.counter ===\n')
print("num_flows: %d" % offloads.num_flows.counter)

print('\n=== restore_hashtbl ===\n')
restore_hashtbl = sample_priv.restore_hashtbl

for i in range(256):
    node = restore_hashtbl[i].first
    while node.value_():
        obj = container_of(node, "struct mlx5_sample_restore", "hlist")
        print("mlx5_sample_restore %lx" % obj.value_())
        mlx5_sample_restore = Object(prog, 'struct mlx5_sample_restore', address=obj.value_())
        print("mlx5_sample_restore.obj_id: %d" % (mlx5_sample_restore.obj_id))
        print(mlx5_sample_restore)
        node = node.next


# mlx5e_priv = get_mlx5e_priv(pf0_name)
# offloads = mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads
# esw_chains_priv = offloads.esw_chains_priv
# mapping_ctx = esw_chains_priv.chains_mapping

mlx5e_priv = get_mlx5e_priv(pf0_name)
offloads = mlx5e_priv.mdev.priv.eswitch.offloads
mapping_ctx = offloads.reg_c0_obj_pool

MLX5_MAPPED_OBJ_SAMPLE = prog['MLX5_MAPPED_OBJ_SAMPLE']
MLX5_MAPPED_OBJ_CHAIN = prog['MLX5_MAPPED_OBJ_CHAIN']

def print_mapping_mapping(mapping):
    if MLX5_MAPPED_OBJ_SAMPLE == mapping.type:
#         print(mapping.type)
        print("\tgroup_id: %d, %x, rate: %d, trunc_size: %d" % \
            (mapping.sample.group_id, mapping.sample.group_id, mapping.sample.rate, mapping.sample.trunc_size))

    if MLX5_MAPPED_OBJ_CHAIN == mapping.type:
        print("\tchain: %d, %x" % (mapping.chain, mapping.chain))

print('\n=== mapping mapping_ctx ===\n')
ht = mapping_ctx.ht
print("mapping_ctx %lx" % mapping_ctx)
for i in range(256):
    for item in hlist_for_each_entry('struct mapping_item', ht[i], 'node'):
        print("mapping id: %d\t" % item.id, end='')
        data = Object(prog, 'struct mlx5_mapped_obj',  address=item.data.address_of_())
        print_mapping_mapping(data)

print('\n=== sample_flow ===\n')
try:
    prog.type('struct mlx5_rep_uplink_priv')
    tc_ht = mlx5e_rep_priv.uplink_priv.tc_ht
except LookupError as x:
    tc_ht = mlx5e_rep_priv.tc_ht

for i, flow in enumerate(hash(tc_ht, 'struct mlx5e_tc_flow', 'node')):
    name = flow.priv.netdev.name.string_().decode()
    flow_attr = flow.attr
    esw_attr = flow_attr.esw_attr[0]
    parse_attr = flow_attr.parse_attr
    print("%-14s mlx5e_tc_flow %lx, cookie: %lx, flags: %x, refcnt: %d" % \
        (name, flow.value_(), flow.cookie.value_(), flow.flags.value_(), flow.refcnt.refs.counter))
    print("chain: %x" % flow_attr.chain, end='\t')
    print("dest_chain: %x" % flow_attr.dest_chain, end='\t')
    print("ft: %x" % flow_attr.ft, end='\t')
    print("dest_ft: %x" % flow_attr.dest_ft, end='\t')
    print("ct_state: %x/%x" % (parse_attr.spec.match_value[57] >> 8, parse_attr.spec.match_criteria[57] >> 8))
    print("mlx5_flow_spec %lx" % parse_attr.spec.address_of_())
    print("action: %x" % flow_attr.action)
    if esw_attr.sample.value_() != 0:
        sample_flow = esw_attr.sample.sample_flow
#         if ct:
#             print(sample_flow.pre_attr)
        print("mlx5_sample_flow %x" % sample_flow)
#         print("fte_id: %d" % sample_flow.fte_id)
#         print(sample_flow)
#         print(sample_flow.pre_attr)
#         print(flow_attr)
#     print("match_criteria_enable: %x" % flow.esw_attr[0].parse_attr.spec.match_criteria_enable)
#     print(flow.esw_attr[0].parse_attr)
    print("")

def print_tunnel_mapping(item):
    print("mapping_item %lx" % item, end='\t')
    print("cnt: %d" % item.cnt, end='\t')
    print("id (tunnel_mapping): %d" % item.id, end='\t')
    key = Object(prog, 'struct tunnel_match_key', address=item.data.address_of_())
#     print(key)
    print("tunnel: keyid: %x" % key.enc_key_id.keyid, end=' ')
    print("ipv4 src: %s" % ipv4(ntohl(key.enc_ipv4.src.value_())), end=' ')
    print("dst: %s" % ipv4(ntohl(key.enc_ipv4.dst.value_())), end=' ')
    print("ifindex: %d" % key.filter_ifindex, end=' ')
    print("port: %x" % key.enc_tp.ports)

print('\n=== tunnel mapping_ctx ===\n')
ht = tunnel_mapping.ht
print("mapping_ctx %lx" % tunnel_mapping)
for i in range(256):
    for item in hlist_for_each_entry('struct mapping_item', ht[i], 'node'):
        print_tunnel_mapping(item)
