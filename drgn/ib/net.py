#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os
import ipaddress
from socket import ntohl

sys.path.append("..")
from lib import *

def _ipv4(be32):
#     return ipaddress.IPv4Address(struct.pack("I", be32.value_()))
    return ipaddress.IPv4Address(be32.value_())

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
    print("ucma_context.id: %x" % ucma_context.id)
#     print(ucma_context)
#     print(ucma_context.file.filp)
#     print(ucma_context.cm_id)   # struct rdma_cm_id
    rdma_id_private = container_of(ucma_context.cm_id, "struct rdma_id_private", "id")

    dst_addr = rdma_id_private.id.route.addr.dst_addr
    dst_addr = cast("struct sockaddr_in *", dst_addr.address_of_())
    print("dst_addr: %s " % ipaddress.IPv4Address(ntohl(dst_addr.sin_addr.s_addr.value_())))

    src_addr = rdma_id_private.id.route.addr.src_addr
    src_addr = cast("struct sockaddr_in *", src_addr.address_of_())
    print("src_addr: %s" % ipaddress.IPv4Address(ntohl(src_addr.sin_addr.s_addr.value_())))

#     print(rdma_id_private.cm_id.ib)
    cm_id_private = container_of(rdma_id_private.cm_id.ib, "struct cm_id_private", "id")
    print(cm_id_private)

#     print(ucma_context.cm_id)
#     print(rdma_id_private)
