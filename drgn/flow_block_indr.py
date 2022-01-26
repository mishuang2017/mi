#!/usr/local/bin/drgn -k

# 14.40499 24260   24260   tc              mlx5e_rep_indr_setup_block
#         b'mlx5e_rep_indr_setup_block+0x1 [mlx5_core]'
#         b'flow_indr_dev_setup_offload+0x6a [kernel]'
#         b'tcf_block_offload_cmd.isra.0+0xf7 [kernel]'
#         b'tcf_block_get_ext+0x150 [kernel]'
#         b'ingress_init+0x75 [sch_ingress]'
#         b'qdisc_create+0x18f [kernel]'
#         b'tc_modify_qdisc+0x14d [kernel]'
#         b'rtnetlink_rcv_msg+0x184 [kernel]'
#         b'netlink_rcv_skb+0x55 [kernel]'
#         b'rtnetlink_rcv+0x15 [kernel]'
#         b'netlink_unicast+0x24f [kernel]'
#         b'netlink_sendmsg+0x233 [kernel]'
#         b'sock_sendmsg+0x65 [kernel]'
#         b'____sys_sendmsg+0x25a [kernel]'
#         b'___sys_sendmsg+0x82 [kernel]'
#         b'__sys_sendmsg+0x62 [kernel]'
#         b'__x64_sys_sendmsg+0x1f [kernel]'
#         b'do_syscall_64+0x38 [kernel]'
#         b'entry_SYSCALL_64_after_hwframe+0x44 [kernel]'

# 5.822219 23244   23244   tc              mlx5e_rep_indr_setup_tc_cb
#         b'mlx5e_rep_indr_setup_tc_cb+0x1 [mlx5_core]'
#         b'fl_hw_replace_filter+0x184 [cls_flower]'
#         b'fl_change+0x6ee [cls_flower]'
#         b'tc_new_tfilter+0x68f [kernel]'
#         b'rtnetlink_rcv_msg+0x33d [kernel]'
#         b'netlink_rcv_skb+0x55 [kernel]'
#         b'rtnetlink_rcv+0x15 [kernel]'
#         b'netlink_unicast+0x24f [kernel]'
#         b'netlink_sendmsg+0x233 [kernel]'
#         b'sock_sendmsg+0x65 [kernel]'
#         b'____sys_sendmsg+0x25a [kernel]'
#         b'___sys_sendmsg+0x82 [kernel]'
#         b'__sys_sendmsg+0x62 [kernel]'
#         b'__x64_sys_sendmsg+0x1f [kernel]'
#         b'do_syscall_64+0x38 [kernel]'
#         b'entry_SYSCALL_64_after_hwframe+0x44 [kernel]'

# rep:
# flow_block_cb cb     : mlx5e_rep_setup_tc_cb,      cb_priv: ffff8b7e47500bc0 (mlx5e_priv)
# vxlan:
# flow_block_cb cb     : mlx5e_rep_indr_setup_tc_cb, cb_priv: ffff8b85d8464a00 (mlx5e_rep_indr_block_priv)

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

mlx5e_priv = lib.get_mlx5_pf0()
mlx5e_rep_priv = mlx5e_priv.ppriv

def print_neigh_hash_entry(n):
    print(n)
#     print("mlx5e_neigh.dst_ip: %s" % n.m_neigh.dst_ip.v6.in6_u.u6_addr8)

def print_encap(e):
    print(e)
#     print("encap_id: %d" % e.encap_id)

print("=== flow_block_indr_dev_list ===")
flow_block_indr_dev_list = prog['flow_block_indr_dev_list']

for flow_indr_dev in list_for_each_entry('struct flow_indr_dev', flow_block_indr_dev_list.address_of_(), 'list'):
    print(flow_indr_dev)
    cb_priv = flow_indr_dev.cb_priv
    mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=cb_priv.value_())
    print("flow_indr_dev.cb_priv:\n\tmlx5e_rep_priv %x" % cb_priv)

print("=== flow_block_indr_list ===")
flow_block_indr_list = prog['flow_block_indr_list']

i = 1
for flow_block_cb in list_for_each_entry('struct flow_block_cb', flow_block_indr_list.address_of_(), 'indr.list'):
    print(i)
    print("flow_block_cb.indr.dev.name: %s" % flow_block_cb.indr.dev.name.string_().decode())
    print("flow_block_cb.indr.cb_priv: mlx5e_rep_priv %x" % flow_block_cb.indr.cb_priv)
    print("flow_block_cb.cb_priv: mlx5e_rep_indr_block_priv %x" % flow_block_cb.cb_priv)
    print(flow_block_cb.indr.cleanup)
    print(flow_block_cb.release)
    print(flow_block_cb)
    i = i + 1

if mlx5e_rep_priv.value_():
    print("=== mlx5e_rep_priv.uplink_priv.tc_indr_block_priv_list ===")
    tc_indr_block_priv_list = mlx5e_rep_priv.uplink_priv.tc_indr_block_priv_list
    for mlx5e_rep_indr_block_priv in list_for_each_entry('struct mlx5e_rep_indr_block_priv', tc_indr_block_priv_list.address_of_(), 'list'):
        print(mlx5e_rep_indr_block_priv)
        print(mlx5e_rep_indr_block_priv.netdev.name)

print("\n=== mlx5e_block_cb_list ===\n")
mlx5e_block_cb_list = prog['mlx5e_block_cb_list']
print(mlx5e_block_cb_list)
for flow_block_cb in list_for_each_entry('struct flow_block_cb', mlx5e_block_cb_list.address_of_(), 'driver_list'):
    print(flow_block_cb)
    i = i + 1

print("\n=== flow_indir_dev_list ===\n")
flow_indir_dev_list = prog['flow_indir_dev_list']
# print(flow_indir_dev_list)

for flow_indir_dev_info in list_for_each_entry('struct flow_indir_dev_info', flow_indir_dev_list.address_of_(), 'list'):
#     print(flow_indir_dev_info)
    print(flow_indir_dev_info.dev.name.string_().decode())
    print(flow_indir_dev_info.binder_type)
    print("net_device %x" % flow_indir_dev_info.dev)
    cb_list = flow_indir_dev_info.cb_list
    for flow_block_offload in list_for_each_entry('struct flow_block_offload', cb_list, 'cb_list'):
        print(flow_block_offload)
    print('')
