#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object
import time
import sys
import os

sys.path.append("..")
from lib import *

# net/sched/act_ct.c
# static struct rhashtable zones_ht;
zones_ht = prog['zones_ht']

for i, flow_table in enumerate(hash(zones_ht, 'struct tcf_ct_flow_table', 'node')):
    print("tcf_ct_flow_table %lx" % flow_table)
    print("nf_flowtable %lx" % flow_table.nf_ft.address_of_())

    print(flow_table.ref)
    # old kernel
#     zone = flow_table.zone
    zone = flow_table.key.zone
    print("zone: %d" % zone)

    nf_ft = flow_table.nf_ft
    cb_list = nf_ft.flow_block.cb_list
    for cb in list_for_each_entry('struct flow_block_cb', cb_list.address_of_(), 'list'):
        print(cb)
        mlx5_ct_ft = Object(prog, 'struct mlx5_ct_ft', address=cb.cb_priv)
        print("\t%s:" % mlx5_ct_ft.ct_priv.netdev.name.string_().decode(), end=' ')
        print("\tcb: %s" % address_to_name(hex(cb.cb)), end='\t')
        print('')
