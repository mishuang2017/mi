#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import socket
import sys
import os

sys.path.append("..")
from lib import *

for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    print(name)
#     if "enp4s0f0" not in name and "vxlan_sys_4789" != name:
#     if "enp4s0f0_1" != name:
#     if "enp4s0f0" != name:
#         continue
#     if "vxlan_sys_4789" != name:
#         continue
    mini_Qdisc = dev.miniq_ingress
    if mini_Qdisc.value_() == 0:
        continue
    tcf_proto = mini_Qdisc.filter_list
    ingress_queue = dev.ingress_queue
    if ingress_queue.value_() == 0:
        continue
    qdisc = ingress_queue.qdisc
#     print(qdisc)
    qdisc_size = prog.type('struct Qdisc').size

#     print("%lx" % qdisc.value_())
    addr = qdisc.value_() + qdisc_size
    ingress_sched_data = Object(prog, 'struct ingress_sched_data', address=addr)
#     print(ingress_sched_data)
    block = ingress_sched_data.block
#     print(block)
    if block.value_() == 0:
        print("0")
        continue

    print("=================================== %s =========================================" % name)
    print("%20s ingress_sched_data %20x\n" % (name, addr))
    print("tcf_block %lx, block index: %d" % (block, block.index))

    for cb in list_for_each_entry('struct tcf_block_cb', block.cb_list.address_of_(), 'list'):
#         print(cb)
        func = cb.cb.value_()
        func = address_to_name(hex(func))
        print("tcf_block_cb cb: %s" % func)

        # on ofed 4.6, priv is the pointer of struct mlx5e_priv

    chain_list_addr = block.chain_list.address_of_()
    for chain in list_for_each_entry('struct tcf_chain', chain_list_addr, 'list'):
        if (chain.value_() == 0):
            print("chain 0, continue")
            continue
        print("------------------------------------------------------------------------------")
        print("tcf_chain %lx, index: %d, %x, refcnt: %d, action_refcnt: %d" % \
             (chain, chain.index, chain.index, chain.refcnt, chain.action_refcnt))
        tcf_proto = chain.filter_chain
        while True:
            print("  tcf_proto %lx, protocol %x, prio %x" %       \
                (tcf_proto.value_(), socket.ntohs(tcf_proto.protocol.value_()),   \
                tcf_proto.prio.value_() >> 16))
            head = Object(prog, 'struct cls_fl_head', address=tcf_proto.root.value_())
#             print("list -H %lx" % head.masks.address_of_())
            for node in radix_tree_for_each(head.handle_idr.idr_rt):
#                 print("%lx" % node[1].value_())
                f = Object(prog, 'struct cls_fl_filter', address=node[1].value_())
                print_cls_fl_filter(f)
            tcf_proto = tcf_proto.next
            if tcf_proto.value_() == 0:
                break
