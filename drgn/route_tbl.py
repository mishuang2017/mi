#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import socket
import sys
import os

sys.path.append(".")
from lib_pedit import *

mlx5e_priv = get_mlx5_pf0()

# struct mlx5_esw_offload
offloads = mlx5e_priv.mdev.priv.eswitch.offloads
route_tbl = offloads.route_tbl

print_mlx5e_tc_flow_flags()

for i in range(256):
    node = route_tbl[i].first
    while node.value_():
        obj = container_of(node, "struct mlx5e_route_entry", "hlist")
        print(obj)
        print("valid: %d" % obj.valid)
        print(ipv4(ntohl((obj.key.endpoint_ip.v4.value_()))))
        head = obj.decap_flows.address_of_()
        print("=== decap_flows ===")
        for mlx5e_tc_flow in list_for_each_entry('struct mlx5e_tc_flow', head, 'decap_routes'):
            print_mlx5e_tc_flow(mlx5e_tc_flow)
        print("=== encap entries ===")
        head = obj.encap_entries.address_of_()
        for mlx5e_encap_entry in list_for_each_entry('struct mlx5e_encap_entry', head, 'route_list'):
            print_mlx5e_tc_flow(mlx5e_tc_flow)
        node = node.next
