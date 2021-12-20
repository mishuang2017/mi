#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
#     if "enp4s0f0" not in name and "vxlan_sys_4789" != name:
#     if "enp4s0f0_1" != name:
#     if "enp4s0f0" != name:
#         continue
#     if "vxlan_sys_4789" != name:
#         continue
    ingress_queue = dev.ingress_queue
    if ingress_queue.value_() == 0:
        continue
    qdisc = ingress_queue.qdisc
    qdisc_size = prog.type('struct Qdisc').size

#     print("%lx" % qdisc.value_())
    addr = qdisc.value_() + qdisc_size
    ingress_sched_data = Object(prog, 'struct ingress_sched_data', address=addr)
#     print(ingress_sched_data)
    block = ingress_sched_data.block
    if block.value_() == 0:
        continue

    print("\n====================================== %s =======================================\n" % name)
#     print("%20s ingress_sched_data %20x\n" % (name, addr))
    print("tcf_block %lx, block index: %d" % (block, block.index))

    if struct_exist("struct flow_block_cb"):
        for cb in list_for_each_entry('struct flow_block_cb', block.flow_block.cb_list.address_of_(), 'list'):
#             print(cb)

            func = cb.cb.value_()
            func = address_to_name(hex(func))
            print("flow_block_cb cb     : %s, cb_priv: %x" % (func, cb.cb_priv))

            release = cb.release.value_()
            release = address_to_name(hex(release))
#             print("flow_block_cb release: %s" % release)

            cb_priv = Object(prog, 'struct mlx5e_rep_indr_block_priv', address=cb.cb_priv.value_())
#             print("mlx5e_rep_indr_block_priv %lx" % cb_priv.address_of_())
#             print(cb_priv)
    else:
        for cb in list_for_each_entry('struct tcf_block_cb', block.cb_list.address_of_(), 'list'):
            print(cb)
            func = cb.cb.value_()
            func = address_to_name(hex(func))
            print("tcf_block_cb cb: %s" % func)

            # ofed 4.7, cb is mlx5e_rep_indr_setup_block_cb
            priv = cb.cb_priv
            priv = Object(prog, 'struct mlx5e_rep_indr_block_priv', address=priv.value_())
#             print(priv)

            # on ofed 4.6, priv is the pointer of struct mlx5e_priv

    chain_list_addr = block.chain_list.address_of_()
    for chain in list_for_each_entry('struct tcf_chain', chain_list_addr, 'list'):
        if (chain.value_() == 0):
            print("chain 0, continue")
            continue
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
