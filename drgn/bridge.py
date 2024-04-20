#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5_pf0()
print(mlx5e_priv.netdev.name)
mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch

mlx5_esw_bridge_offloads = mlx5_eswitch.br_offloads
# print(mlx5_esw_bridge_offloads)

# exit(0)
# ingress_ft is global
# egress_ft is per bridge

print("=== mlx5_esw_bridge_offloads ingress ===\n")
print("ingress_vlan_fg   %x" % mlx5_esw_bridge_offloads.ingress_vlan_fg)
# print("ingress_filter_fg %x" % mlx5_esw_bridge_offloads.ingress_filter_fg)
print("ingress_mac_fg    %x" % mlx5_esw_bridge_offloads.ingress_mac_fg)
ingress_ft = mlx5_esw_bridge_offloads.ingress_ft
print("ingress_ft        %x" % ingress_ft.value_())
skip_ft = mlx5_esw_bridge_offloads.skip_ft
print("skip_ft           %x" % skip_ft)
# flow_table("ingress_ft", ingress_ft)


print("\n=== mlx5_esw_bridge egress ===\n")

def print_mlx5_esw_bridge(bridge):
    print("bridge.ifindex: %d\n" % bridge.ifindex)
    egress_ft = bridge.egress_ft
    print("egress_vlan_fg %x" % bridge.egress_vlan_fg)
    print("egress_mac_fg  %x" % bridge.egress_mac_fg)
    print("egress_miss_fg %x" % bridge.egress_miss_fg)
    print("egress_ft      %x" % egress_ft.value_())
#     flow_table("egress_ft", egress_ft)

    print("\n=== mlx5_esw_bridge mlx5_esw_bridge_fdb_entry ===\n")
    fdb_list = bridge.fdb_list
    for fdb_entry in list_for_each_entry('struct mlx5_esw_bridge_fdb_entry', fdb_list.address_of_(), 'list'):
        print("fdb_entry: %x" % fdb_entry)
        print("key.addr: %s, vport_num: %d, dev name: %s, lastuse: %lx" % ((mac((fdb_entry.key.addr))), fdb_entry.vport_num,
            fdb_entry.dev.name.string_().decode(), fdb_entry.lastuse))
#         print("\n--- fdb_entry.ingress_handle ---")
#         print_mlx5_flow_handle(fdb_entry.ingress_handle)
#         print("\n--- fdb_entry.egress_handle ---")
#         print_mlx5_flow_handle(fdb_entry.egress_handle)

#     print("\n=== mlx5_esw_bridge.egress_miss_handle ==\n")
#     egress_miss_handle = mlx5_esw_bridge.egress_miss_handle
#     print(egress_miss_handle)
    ageing_time = bridge.ageing_time
    print("ageing_time: %d" % ageing_time)

bridges = mlx5_esw_bridge_offloads.bridges
for mlx5_esw_bridge in list_for_each_entry('struct mlx5_esw_bridge', bridges.address_of_(), 'list'):
    print_mlx5_esw_bridge(mlx5_esw_bridge)

# exit(0)

MLX5_ESW_BRIDGE_PORT_FLAG_PEER = prog['MLX5_ESW_BRIDGE_PORT_FLAG_PEER']

def print_vlan(vlans):
    for node in radix_tree_for_each(vlans.address_of_()):
        vlan = Object(prog, 'struct mlx5_esw_bridge_vlan', address=node[1].value_())
        print(vlan)

print("\n=== mlx5_esw_bridge ports ===\n")
print("MLX5_ESW_BRIDGE_PORT_FLAG_PEER = %d" % MLX5_ESW_BRIDGE_PORT_FLAG_PEER)
ports = mlx5_esw_bridge_offloads.ports.address_of_()
for node in radix_tree_for_each(ports):
    print('--------------------------start------------------------------------')
    port = Object(prog, 'struct mlx5_esw_bridge_port', address=node[1].value_())
#     print(port)
    print("port->vport_num: %d, esw_owner_vhca_id: %d, flags: %x" %
        (port.vport_num, port.esw_owner_vhca_id, port.flags))
#     print_vlan(port.vlans)
#     mlx5_esw_bridge = port.bridge
#     print_mlx5_esw_bridge(mlx5_esw_bridge)
#     flow_table("port.mcast.ft", port.mcast.ft)
#     print('--------------------------end------------------------------------')

print("\n=== switchdev_notif_chain ==\n")
switchdev_notif_chain = prog['switchdev_notif_chain']
notifier_block = switchdev_notif_chain.head

while True:
    if notifier_block.value_() == 0:
        break
#     print(notifier_block)
    print(address_to_name(hex(notifier_block.notifier_call)))
#     if notifier_block.notifier_call.value_() == prog['mlx5_esw_bridge_switchdev_event'].address_of_().value_():
#         mlx5_esw_bridge_offloads = container_of(notifier_block, "struct mlx5_esw_bridge_offloads", "nb")
#         print(mlx5_esw_bridge_offloads)
    notifier_block = notifier_block.next


# 14.73379 455917  455917  kworker/u20:4   mlx5_add_flow_rules
#         mlx5_add_flow_rules
#         mlx5_esw_bridge_fdb_entry_init
#         mlx5_esw_bridge_fdb_create
#         mlx5_esw_bridge_switchdev_fdb_event_work
#         process_one_work+0x249 [kernel]'
#         worker_thread+0x52 [kernel]'
#         kthread+0x174 [kernel]'
#         ret_from_fork+0x22 [kernel]'

#         queue_work(mlx5_esw_bridge_switchdev_fdb_event_work)
#         mlx5_esw_bridge_switchdev_event
#         call_switchdev_notifiers(SWITCHDEV_FDB_ADD_TO_DEVICE)

# 10707.67 0       0       swapper/0       br_switchdev_fdb_notify
#         br_switchdev_fdb_notify
#         br_fdb_update
#         br_handle_frame_finish
#         br_nf_hook_thresh
#         br_nf_pre_routing_finish
#         br_nf_pre_routing
#         nf_hook_bridge_pre
#         br_handle_frame
#         b'__netif_receive_skb_core+0x2bf [kernel]'
#         b'__netif_receive_skb_list_core+0x12a [kernel]'
#         b'__netif_receive_skb_list+0x102 [kernel]'
#         b'netif_receive_skb_list_internal+0x12a [kernel]'
#         b'napi_complete_done+0x7a [kernel]'
#         b'mlx5e_napi_poll+0x1b9 [mlx5_core]'
#         b'__napi_poll+0x2f [kernel]'
#         b'net_rx_action+0x282 [kernel]'
#         b'__softirqentry_text_start+0x169 [kernel]'
#         b'__irq_exit_rcu+0xe9 [kernel]'
#         b'irq_exit_rcu+0xe [kernel]'
#         b'common_interrupt+0xc2 [kernel]'
#         b'asm_common_interrupt+0x1e [kernel]'
#         b'default_idle+0x14 [kernel]'
#         b'arch_cpu_idle+0x15 [kernel]'
#         b'default_idle_call+0x5e [kernel]'
#         b'cpuidle_idle_call+0x16f [kernel]'
#         b'do_idle+0x92 [kernel]'
#         b'cpu_startup_entry+0x20 [kernel]'
#         b'rest_init+0x170 [kernel]'
#         b'arch_call_rest_init+0xe [kernel]'
#         b'start_kernel+0x472 [kernel]'
#         b'x86_64_start_reservations+0x24 [kernel]'
#         b'x86_64_start_kernel+0x8e [kernel]'
#         b'secondary_startup_64_no_verify+0xc3 [kernel]'
