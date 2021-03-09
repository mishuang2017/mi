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

    zone = flow_table.zone
    print("zone: %d" % zone)

    nf_ft = flow_table.nf_ft
    ft_ht = nf_ft.rhashtable
    for j, tuple_rhash in enumerate(hash(ft_ht, 'struct flow_offload_tuple_rhash', 'node')):
        print_tuple_rhash_tuple(tuple_rhash)
    print('')
