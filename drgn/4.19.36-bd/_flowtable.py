#!/usr/local/bin/drgn -k

from drgn import container_of
from drgn.helpers.linux import *
from drgn import Object

import sys
import os

sys.path.append("..")
from lib import *

try:
    table_addr = prog['_flowtable']
except LookupError as x:
    print("no _flowtable")
    sys.exit(1)

# table_addr = lib.name_to_address("_flowtable")
if table_addr.value_() == 0:
    print("_flowtable is not initialized")
    sys.exit(1)

flow_offload_table = Object(prog, 'struct flow_offload_table', address=table_addr)
# print(table)

entries = []
for i, flow in enumerate(hash(flow_offload_table.rhashtable, 'struct flow_offload_tuple_rhash', 'node')):
    print("index: %d:" % i, end=' ')
    flow_offload_tuple_rhash = Object(prog, 'struct flow_offload_tuple_rhash', address=flow.value_())
    dir = flow_offload_tuple_rhash.tuple.dst.dir

    size = prog.type('struct flow_offload_tuple_rhash').size
#     print("size: %lx" % (size))
    print("flow_offload_tuple_rhash %lx" % (flow_offload_tuple_rhash.address_of_()))

    if dir == 0:
        offset = 0
    if dir == 1:
        offset = size

    flow_offload_entry = flow_offload_tuple_rhash.address_of_().value_() - offset
    if flow_offload_entry not in entries:
        entries.append(flow_offload_entry)

print("")
print("num of flow_offload_entry entries (two flow_offload_tuple_rhash share one flow_offload_entry): %d" % len(entries))
print("")

for i in entries:
    flow_offload_entry = Object(prog, 'struct flow_offload_entry', address=i)
    print("flow_offload_entry %lx" % flow_offload_entry.address_of_().value_())

#     nr_tc_flows = flow_offload_entry.nr_tc_flows.refs.counter.value_()
#     print("nr_tc_flows %d" % nr_tc_flows)
    deps = flow_offload_entry.deps
    for flow in list_for_each_entry('struct mlx5e_tc_flow', deps.address_of_(), 'nft_node'):
        name = flow.priv.netdev.name.string_().decode()
        lastuse = flow.dummy_counter.cache.lastuse
        refcnt = flow.refcnt.refs.counter.value_()
        print("\t%-10s: mlx5e_tc_flow %lx, lastuse: %ld, refcnt: %d" % (name, flow.value_(), lastuse / 1000, refcnt))
