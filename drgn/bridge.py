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

print("=== mlx5_esw_bridge_offloads ingress ===")
ingress_ft = mlx5_esw_bridge_offloads.ingress_ft
flow_table("ingress_ft", ingress_ft)

# skip_ft = mlx5_esw_bridge_offloads.skip_ft
# flow_table("skip_ft", skip_ft)

print("\n=== mlx5_esw_bridge egress ===")

def print_mlx5_esw_bridge(bridge):
#     print(bridge)
    egress_ft = bridge.egress_ft
    flow_table("egress_ft", egress_ft)

#     fdb_list = bridge.fdb_list
#     for fdb_entry in list_for_each_entry('struct mlx5_esw_bridge_fdb_entry', fdb_list.address_of_(), 'list'):
#         print(fdb_entry)
#         print("=== fdb_entry.ingress_handle ===")
#         print_mlx5_flow_handle(fdb_entry.ingress_handle)
#         print("=== fdb_entry.egress_handle ===")
#         print_mlx5_flow_handle(fdb_entry.egress_handle)

bridges = mlx5_esw_bridge_offloads.bridges
for mlx5_esw_bridge in list_for_each_entry('struct mlx5_esw_bridge', bridges.address_of_(), 'list'):
    print_mlx5_esw_bridge(mlx5_esw_bridge)

sys.exit(0)

ports = mlx5_esw_bridge_offloads.ports
for node in radix_tree_for_each(ports):
    port = Object(prog, 'struct mlx5_esw_bridge_port', address=node[1].value_())
#     print(port)
    mlx5_esw_bridge = port.bridge
#     print(mlx5_esw_bridge)
    print_mlx5_esw_bridge(mlx5_esw_bridge)
