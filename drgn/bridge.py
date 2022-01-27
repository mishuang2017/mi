#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5_pf0()
mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch

mlx5_esw_bridge_offloads = mlx5_eswitch.br_offloads
# print(mlx5_esw_bridge_offloads)

# ingress_ft is global
# egress_ft is per bridge

print("=== mlx5_esw_bridge_offloads ingress ===\n")
ingress_ft = mlx5_esw_bridge_offloads.ingress_ft
print("ingress_ft %x" % ingress_ft.value_())
flow_table("ingress_ft", ingress_ft)

# skip_ft = mlx5_esw_bridge_offloads.skip_ft
# flow_table("skip_ft", skip_ft)

print("\n=== mlx5_esw_bridge egress ===\n")

def print_mlx5_esw_bridge(bridge):
    print("bridge.ifindex: %d" % bridge.ifindex)
    egress_ft = bridge.egress_ft
    print("egress_ft %x\n" % egress_ft.value_())
    flow_table("egress_ft", egress_ft)

#     fdb_list = bridge.fdb_list
#     for fdb_entry in list_for_each_entry('struct mlx5_esw_bridge_fdb_entry', fdb_list.address_of_(), 'list'):
#         print(fdb_entry)
#         print("\n=== fdb_entry.ingress_handle ===")
#         print_mlx5_flow_handle(fdb_entry.ingress_handle)
#         print("=== fdb_entry.egress_handle ===")
#         print_mlx5_flow_handle(fdb_entry.egress_handle)

print("\n=== mlx5_esw_bridge bridges ===\n")

bridges = mlx5_esw_bridge_offloads.bridges
for mlx5_esw_bridge in list_for_each_entry('struct mlx5_esw_bridge', bridges.address_of_(), 'list'):
    print_mlx5_esw_bridge(mlx5_esw_bridge)

print("\n=== mlx5_esw_bridge ports ===\n")
ports = mlx5_esw_bridge_offloads.ports.address_of_()
for node in radix_tree_for_each(ports):
    port = Object(prog, 'struct mlx5_esw_bridge_port', address=node[1].value_())
    print("port->vport_num: %d" % port.vport_num)
#     mlx5_esw_bridge = port.bridge
#     print_mlx5_esw_bridge(mlx5_esw_bridge)

print("\n=== switchdev_notif_chain ==\n")
switchdev_notif_chain = prog['switchdev_notif_chain']
notifier_block = switchdev_notif_chain.head

while True:
    if notifier_block.value_() == 0:
        break
    print(address_to_name(hex(notifier_block.notifier_call)))
    if notifier_block.notifier_call.value_() == prog['mlx5_esw_bridge_switchdev_event'].address_of_().value_():
        mlx5_esw_bridge_offloads = container_of(notifier_block, "struct mlx5_esw_bridge_offloads", "nb")
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
