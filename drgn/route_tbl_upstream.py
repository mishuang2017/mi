#!/usr/local/bin/drgn -k

# mlx5e_tc_esw_init
#         mlx5e_tc_tun_init
#                 mlx5e_tc_tun_fib_event
#                         mlx5e_init_fib_work_ipv4
#                                 mlx5e_tc_init_fib_work
#                                 mlx5e_route_lookup_for_update
#                                         mlx5e_route_get
#                         queue_work(priv->wq, &fib_work->work)
#                                 mlx5e_tc_fib_event_work
 
from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import socket
import sys
import os

sys.path.append(".")
from lib_pedit import *

mlx5e_rep_priv = get_mlx5e_rep_priv()
uplink_priv = mlx5e_rep_priv.uplink_priv
mlx5e_tc_tun_encap = uplink_priv.encap

route_tbl = mlx5e_tc_tun_encap.route_tbl

print_mlx5e_tc_flow_flags()

n=1
for i in range(256):
    node = route_tbl[i].first
    while node.value_():
        print("=================== %d ==================" % n)
        obj = container_of(node, "struct mlx5e_route_entry", "hlist")
        print(obj)
        print("valid: %d" % obj.flags)
        print(ipv4(ntohl((obj.key.endpoint_ip.v4.value_()))))
        head = obj.decap_flows.address_of_()
        print("=== decap_flows ===")
        for mlx5e_tc_flow in list_for_each_entry('struct mlx5e_tc_flow', head, 'decap_routes'):
            print_mlx5e_tc_flow(mlx5e_tc_flow)
        print("=== encap entries ===")
        head = obj.encap_entries.address_of_()
        for mlx5e_encap_entry in list_for_each_entry('struct mlx5e_encap_entry', head, 'route_list'):
#             print(mlx5e_encap_entry)
            print_mlx5e_encap_entry(mlx5e_encap_entry)
        node = node.next
        n = n + 1
