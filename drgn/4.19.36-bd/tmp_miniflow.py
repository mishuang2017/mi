#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import socket
import sys
import os

sys.path.append("..")
from lib import *

def print_miniflow_list(flow):
    j = 0
    for mlx5e_miniflow_node in list_for_each_entry('struct mlx5e_miniflow_node', flow.miniflow_list.address_of_(), 'node'):
        print("\t%d: mlx5e_miniflow %lx" % (j, mlx5e_miniflow_node.miniflow.value_()))
        j = j + 1

miniflow_list = []

def print_nf_conntrack_tuple(tuple):
    print("src ip  : %s" % ipv4(ntohl(tuple.src.u3.ip.value_())))
    print("src port: %d" % ntohs(tuple.src.u.all.value_()))
    print("dst ip  : %s" % ipv4(ntohl(tuple.dst.u3.ip.value_())))
    print("dst port: %d" % ntohs(tuple.dst.u.all.value_()))

def print_mlx5e_ct_tuple(k, tuple):
    print("\n=== mlx5e_ct_tuple start ===")
#     print("%d: ipv4: %s" % (k, ipv4(ntohl(tuple.ipv4.value_()))))
#     print("%d: zone: %d" % (k, tuple.zone.id))
#     print("%d: nat: 0x%lx" % (k, tuple.nat))
#     print("%d: mlx5e_tc_flow %lx, refcnt: %d" % (k, tuple.flow, tuple.flow.refcnt.refs.counter.value_()))
    print_nf_conntrack_tuple(tuple.tuple)
    print("=== mlx5_ct_tuple end ===\n")

# for old 4.20 kernel
# for flow in list_for_each_entry('struct mlx5e_tc_flow', prog['ct_list'].address_of_(), 'nft_node'):
#     print("%s: mlx5e_tc_flow: %lx" % (flow.priv.netdev.name.string_().decode(), flow.value_()))
#     fc = flow.dummy_counter
#     p = fc.lastpackets
#     b = fc.lastbytes
#     print("packets: %d, bytes: %d" % (p, b))
#     for mini in list_for_each_entry('struct mlx5e_miniflow', flow.miniflow_list.address_of_(), 'node'):
#         mlx5e_miniflow_node = Object(prog, 'struct mlx5e_miniflow_node', address=mini.value_())
#         miniflow = mlx5e_miniflow_node.miniflow
#         print("mlx5e_miniflow: %lx" % miniflow)
#         if miniflow not in miniflow_list:
#             miniflow_list.append(miniflow)

mlx5e_rep_priv = get_mlx5e_rep_priv()
mf_ht = mlx5e_rep_priv.mf_ht

j = 0

for i, flow in enumerate(hash(mf_ht, 'struct mlx5e_miniflow', 'node')):
    print("%3d: mlx5e_miniflow %lx, nr_ct_tuples: %d, nr_flows: %d" % \
        (i, flow.value_(), flow.nr_ct_tuples, flow.nr_flows))
    miniflow_list.append(flow)
    j = i

j=j+1
print("total: %d" % (j))

print('')
for i in miniflow_list:
#     print("+++++++++++++++++++++ start ++++++++++++++++++++\n")
    name = i.priv.netdev.name.string_().decode()
#     print("cookie: %lx" % i.cookie)     # pointer of skb
#     print('{0}'.format(i.tuple))

    if name.startswith("enp4s0f0"):
        flow = i.flow
        print("miniflow->flow: mlx5e_tc_flow %lx, refcnt: %d, flags: %x" % \
            (flow, flow.refcnt.refs.counter, flow.flags.counter))
        fc = flow.esw_attr[0].counter
#         print(fc)
#         lib.print_mlx5_flow_handle(flow.rule[0])
#     if name == "enp4s0f0_1":

        for j in range(8):
            flow = i.path.flows[j]
            if flow:
#                 print("\n####################### %d ####################\n" % j)
                print("%12s: path.flows[%d]: mlx5e_tc_flow %lx, flags: %x" % (name, j, flow.value_(), flow.flags.counter))
#                 print_miniflow_list(flow)
                continue
                attr = flow.esw_attr[0]
                fc = flow.dummy_counter
                p = fc.lastpackets
                b = fc.lastbytes
                print("mlx5_fc: %lx, packets: %d, bytes: %d" % (fc, p, b))
                print("action: %4x, chain: %d" % (attr.action, attr.chain))
                print('')

                lastuse = flow.dummy_counter.cache.lastuse
                print("mlx5e_tc_flow %lx, lastuse: %lx" % (flow.value_(), lastuse / 1000))

            continue
            cookie = i.path.cookies[j]
            if cookie:
                addr = cookie.value_()
                print("cookie %lx" % addr)
                if (addr & 1):
                    print("=========== %d %s %s ==========" % (j, name, "nf_conntrack_tuple"))
                    addr = addr & ~0x1
                    nf_conntrack_tuple = Object(prog, 'struct nf_conntrack_tuple', address=addr)
                    print_nf_conntrack_tuple(nf_conntrack_tuple)
                else:
                    print("=========== %d %s %s ==========" % (j, name, "cls_fl_filter"))
                    cls_fl_filter = Object(prog, 'struct cls_fl_filter', address=addr)
                    print_cls_fl_filter(cls_fl_filter)

        continue
        n = i.nr_ct_tuples
        print("\nnr_ct_tuples: %x" % n)
        for k in range(n):
#             print(i.ct_tuples[k])
            print_mlx5e_ct_tuple(k, i.ct_tuples[k])
        print("+++++++++++++++++++++ end ++++++++++++++++++++\n")
