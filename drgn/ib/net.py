#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

sys.path.append("..")
from lib import *

# net_namespace_list = prog['net_namespace_list']
# for net in list_for_each_entry('struct net', net_namespace_list.address_of_(), 'list'):
#     dev_base_head = net.dev_base_head.address_of_()

NFPROTO_NUMPROTO = prog['NFPROTO_NUMPROTO']

gen = prog['init_net'].gen
id = prog['cma_pernet_id']
# print("cma_pernet_id: %d" % id)
ptr = gen.ptr[id]
cma_pernet = Object(prog, 'struct cma_pernet', address=ptr.value_())
# print(cma_pernet)

tcp_ps = cma_pernet.tcp_ps
# print(tcp_ps)
for node in radix_tree_for_each(tcp_ps.address_of_()):
#     print(node)
    rdma = Object(prog, 'struct rdma_bind_list', address=node[1].value_())
#     print(rdma)
    for rdma_id_private in hlist_for_each_entry('struct rdma_id_private', rdma.owners, 'node'):
        print("rdma_id_private %x" % rdma_id_private)
#         print(rdma_id_private)

ctx_table = prog['ctx_table']
# print(ctx_table)
for node in radix_tree_for_each(ctx_table.address_of_()):
    ucma_context = Object(prog, 'struct ucma_context', address=node[1].value_())
    print(ucma_context.id)
#     print(ucma_context.file.filp)
#     print(ucma_context.cm_id)
    rdma_id_private = container_of(ucma_context.cm_id, "struct rdma_id_private", "id")
    print(rdma_id_private)
    print(rdma_id_private.cm_id.ib)
    cm_id_private = container_of(rdma_id_private.cm_id.ib, "struct cm_id_private", "id")
#     print(cm_id_private)
