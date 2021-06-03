#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

import sys
import os

sys.path.append("..")
# from lib import *
from lib_pedit import *

mlx5e_rep_priv = get_mlx5e_rep_priv()
ct_priv = mlx5e_rep_priv.uplink_priv.ct_priv
tunnel_mapping = mlx5e_rep_priv.uplink_priv.tunnel_mapping
# labels_mapping = ct_priv.labels_mapping
zone_mapping = ct_priv.zone_mapping

print("=== mlx5e_rep_priv.uplink_priv.ct_priv.mod_hdr_tbl ===")
mod_hdr_tbl = ct_priv.mod_hdr_tbl
ht = mod_hdr_tbl.hlist
for i in range(256):
    for mh in hlist_for_each_entry('struct mlx5e_mod_hdr_handle', ht[i], 'mod_hdr_hlist'):
        print("--- %d ---" % i)
        print("\tmlx5e_mod_hdr_handle.refcnt: %d" % mh.refcnt.refs.counter)
        print_mod_hdr_key(mh.key)

# print('\n=== labels_mapping ===\n')
# ht = labels_mapping.ht
# print("mapping_ctx %lx" % labels_mapping)
# for i in range(256):
#     for item in hlist_for_each_entry('struct mapping_item', ht[i], 'node'):
#         ct_labels_id = Object(prog, 'u32 *', address=item.data.address_of_())
#         print("cnt: %d, id: %d, data: %d" % (item.cnt, item.id, ct_labels_id))

print("=== mlx5e_rep_priv.uplink_priv.ct_priv.ct ===")
# print("mlx5_flow_table %lx" % ct_priv.ct)
flow_table("ct_priv.ct", ct_priv.ct)

print("=== mlx5e_rep_priv.uplink_priv.ct_priv.ct_nat ===")
flow_table("ct_priv.ct_nat", ct_priv.ct_nat)

print("=== mlx5e_rep_priv.uplink_priv.ct_priv.post_ct ===")
# print("mlx5_flow_table %lx" % ct_priv.post_ct)
flow_table("ct_priv.post_ct", ct_priv.post_ct)

###############################

fte_ids = ct_priv.fte_ids

print("=== mlx5e_rep_priv.uplink_priv.ct_priv.fte_ids ===")
# idr
# for node in radix_tree_for_each(fte_ids.idr_rt):
# xarray
for node in radix_tree_for_each(fte_ids):
    mlx5_ct_flow = Object(prog, 'struct mlx5_ct_flow', address=node[1].value_())
    print("mlx5_ct_flow %lx" % mlx5_ct_flow.address_of_())
    print("\tfte_id: %d" % mlx5_ct_flow.fte_id, end='\t')
    print("chain_mapping: %d" % mlx5_ct_flow.chain_mapping, end='\t')
    print('')

    print("\tmlx5_ct_flow.pre_ct_attr")
    print_mlx5_esw_flow_attr(mlx5_ct_flow.pre_ct_attr)

    print("\tmlx5_ct_flow.post_ct_attr")
    print_mlx5_esw_flow_attr(mlx5_ct_flow.post_ct_attr)

    print("\tmlx5_ct_flow.pre_ct_rule")
    print_mlx5_flow_handle(mlx5_ct_flow.pre_ct_rule)

    print("\tmlx5_ct_flow.post_ct_rule")
    print_mlx5_flow_handle(mlx5_ct_flow.post_ct_rule)

###############################

tuple_ids = ct_priv.tuple_ids
# print(tuple_ids)

print("=== mlx5e_rep_priv.uplink_priv.ct_priv.tuple_ids ===")
for node in radix_tree_for_each(tuple_ids):
    mlx5_ct_zone_rule = Object(prog, 'struct mlx5_ct_zone_rule', address=node[1].value_())
    print("tupleid: %x" % mlx5_ct_zone_rule.tupleid)

################################

# print(ct_priv)
print("\n=== mlx5e_rep_priv.uplink_priv.ct_priv.zone_ht ===")
zone_ht = ct_priv.zone_ht
# print(zone_ht)

for i, mlx5_ct_ft in enumerate(hash(zone_ht, 'struct mlx5_ct_ft', 'node')):
    print("mlx5_ct_ft %lx" % mlx5_ct_ft)
    print("zone: %d" % mlx5_ct_ft.zone)

    print("nf_flowtable %lx" % mlx5_ct_ft.nf_ft)
    print("mlx5_ct_ft.ct_entries_ht:")
    ct_entries_ht = mlx5_ct_ft.ct_entries_ht
    for j, mlx5_ct_entry in enumerate(hash(ct_entries_ht, 'struct mlx5_ct_entry', 'node')):
        print("mlx5_ct_entry %lx" % mlx5_ct_entry)
        print("\tcookie is flow_offload_tuple %lx" % mlx5_ct_entry.cookie)
        print("\trestore_cookie is 'ct | ctinfo' %lx" % mlx5_ct_entry.restore_cookie)
        print('')

        for k in range(2):
            mlx5_ct_zone_rule = mlx5_ct_entry.zone_rules[k]
            print("\tmlx5_ct_entry.zone_rules[%d]" % k)
            print("\tmlx5_ct_zone_rule %lx" % mlx5_ct_zone_rule.address_of_())
            print("\tmlx5_esw_flow_attr %lx" % mlx5_ct_zone_rule.attr.address_of_())
#             print_mlx6_esw_flow_attr(mlx5_ct_zone_rule.attr)
#             mlx5_flow_handle = mlx5_ct_zone_rule.rule
#             nat = mlx5_ct_zone_rule.nat
#             print("\tmlx5_ct_entry.zone_rules[%d].rule: nat: %d(tupleid is unique for mlx5_ct_entry.mlx5_ct_zone_rule[nat], it is used to restore ctinfo)" % (k, nat))
#             print("\t\tmlx5_ct_zone_rule.rule")
#             print_mlx5_flow_handle(mlx5_flow_handle)
        print('')

    flow_table("mlx5_ct_ft.pre_ct.ft", mlx5_ct_ft.pre_ct.ft)
    flow_table("mlx5_ct_ft.pre_ct_nat.ft", mlx5_ct_ft.pre_ct_nat.ft)

#         print("\tmlx5_ct_entry.zone_rules[1].rule")
#         mlx5_flow_handle = mlx5_ct_entry.zone_rules[1].rule
#         print_mlx5_flow_handle(mlx5_flow_handle)
#         print(mlx5_ct_entry.flow_rule)

#     ct_entries_list = mlx5_ct_ft.ct_entries_list
#     for mlx5_ct_entry in list_for_each_entry('struct mlx5_ct_entry', ct_entries_list.address_of_(), 'list'):
#         print(mlx5_ct_entry)

###############################

def print_tunnel_mapping(item):
    print("mapping_item %lx" % item, end='\t')
    print("cnt: %d" % item.cnt, end='\t')
    print("id (tunnel_mapping): %d" % item.id, end='\t')
    key = Object(prog, 'struct tunnel_match_key', address=item.data.address_of_())
#     print(key)
    print("tunnel: keyid: %x" % key.enc_key_id.keyid, end=' ')
    print("ipv4 src: %s" % ipv4(ntohl(key.enc_ipv4.src.value_())), end=' ')
    print("dst: %s" % ipv4(ntohl(key.enc_ipv4.dst.value_())), end=' ')
    print("ifindex: %d" % key.filter_ifindex)

print('\n=== tunnel mapping_ctx ===\n')
ht = tunnel_mapping.ht
print("mapping_ctx %lx" % tunnel_mapping)
for i in range(256):
    for item in hlist_for_each_entry('struct mapping_item', ht[i], 'node'):
        print_tunnel_mapping(item)

print('\n=== zone mapping_ctx ===\n')
ht = zone_mapping.ht
print("mapping_ctx %lx" % zone_mapping)
for i in range(256):
    for item in hlist_for_each_entry('struct mapping_item', ht[i], 'node'):
        data = Object(prog, 'u8 *', address=item.data.address_of_())
        print("id: %d, data: %d" % (item.id, data))
