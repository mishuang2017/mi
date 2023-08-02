#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

sys.path.append("..")
from lib import *

# net/netfilter/nf_flow_table_core.c
# static LIST_HEAD(flowtables);

flowtables = prog['flowtables']

NF_FLOWTABLE_HW_OFFLOAD = prog['NF_FLOWTABLE_HW_OFFLOAD']
NF_FLOWTABLE_COUNTER = prog['NF_FLOWTABLE_COUNTER']

for nf_ft in list_for_each_entry('struct nf_flowtable', flowtables.address_of_(), 'list'):
    print("nf_flowtable %lx" % nf_ft)
    print("nf_flowtable.flags: %x, NF_FLOWTABLE_HW_OFFLOAD: %x, NF_FLOWTABLE_COUNTER %d" % (nf_ft.flags, NF_FLOWTABLE_HW_OFFLOAD, NF_FLOWTABLE_COUNTER))
#     print(nf_ft)
    print(nf_ft.type)
    gc_work_func = nf_ft.gc_work.work.func
    print("nf_ft.gc_work.work.func: %s" % address_to_name(hex(gc_work_func)))
    cb_list = nf_ft.flow_block.cb_list
    for cb in list_for_each_entry('struct flow_block_cb', cb_list.address_of_(), 'list'):
#         print(cb)
        mlx5_ct_ft = Object(prog, 'struct mlx5_ct_ft *', address=cb.cb_priv.address_of_().value_())
        print("\t%s:" % mlx5_ct_ft.ct_priv.netdev.name.string_().decode(), end=' ')
        print("\tcb: %s" % address_to_name(hex(cb.cb)), end='\t')
        print("\tmlx5_ct_ft %lx" % cb.cb_priv, end='\t')
#         print("\tmlx5_ct_ft.zone_restore_id: %d" % mlx5_ct_ft.zone_restore_id)
        print('')
 
    tuple_hash = nf_ft.rhashtable
    for i, rhash in enumerate(hash(tuple_hash, 'struct flow_offload_tuple_rhash', 'node')):
        print("flow_offload_tuple %lx" % rhash.tuple.address_of_())
        print_tuple_rhash_tuple(rhash)
