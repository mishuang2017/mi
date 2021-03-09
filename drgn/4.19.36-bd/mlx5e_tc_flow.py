#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

import sys
import os

sys.path.append("..")
from lib import *

mlx5e_rep_priv = get_mlx5e_rep_priv()

print("MLX5E_TC_FLOW_INGRESS   %10x" % (prog['MLX5E_TC_FLOW_INGRESS'].value_()))
print("MLX5E_TC_FLOW_EGRESS    %10x" % (prog['MLX5E_TC_FLOW_EGRESS'].value_()))
print("MLX5E_TC_FLOW_ESWITCH   %10x" % (prog['MLX5E_TC_FLOW_ESWITCH'].value_()))
print("MLX5E_TC_FLOW_OFFLOADED %10x" % (prog['MLX5E_TC_FLOW_OFFLOADED'].value_()))
print("MLX5E_TC_FLOW_SIMPLE    %10x" % (prog['MLX5E_TC_FLOW_SIMPLE'].value_()))
print("MLX5E_TC_FLOW_CT        %10x" % (prog['MLX5E_TC_FLOW_CT'].value_()))

print('')
print("MLX5_MATCH_OUTER_HEADERS     %10x" % prog['MLX5_MATCH_OUTER_HEADERS'].value_())
print("MLX5_MATCH_MISC_PARAMETERS   %10x" % prog['MLX5_MATCH_MISC_PARAMETERS'].value_())
print("MLX5_MATCH_MISC_PARAMETERS_2 %10x" % prog['MLX5_MATCH_MISC_PARAMETERS_2'].value_())

try:
    prog.type('struct mlx5_rep_uplink_priv')
    tc_ht = mlx5e_rep_priv.uplink_priv.tc_ht
except LookupError as x:
    tc_ht = mlx5e_rep_priv.tc_ht

for i, flow in enumerate(hash(tc_ht, 'struct mlx5e_tc_flow', 'node')):
    name = flow.priv.netdev.name.string_().decode()
    print("%-14s mlx5e_tc_flow %lx, cookie: %lx, flags: %x, refcnt: %d" % \
        (name, flow.value_(), flow.cookie.value_(), flow.flags.counter.value_(), flow.refcnt.refs.counter))
    print("chain: %x" % flow.esw_attr[0].chain, end='\t')
    print("dest_chain: %x" % flow.esw_attr[0].dest_chain, end='\t')
#     print("ct_state: %x/%x" % (flow.esw_attr[0].parse_attr.spec.match_value[57] >> 8, \
#         flow.esw_attr[0].parse_attr.spec.match_criteria[57] >> 8))
    print("mlx5_flow_spec %lx" % flow.esw_attr[0].parse_attr.spec.address_of_())
    print("action: %x" % flow.esw_attr[0].action)
#     print("match_criteria_enable: %x" % flow.esw_attr[0].parse_attr.spec.match_criteria_enable)
#     print(flow.esw_attr[0].parse_attr)
#     print(flow.esw_attr[0])
    print("")

#     tun_info = flow.esw_attr[0].parse_attr.tun_info
#     if tun_info.value_():
#         print_tun(tun_info)
#         print(tun_info)

#     continue
#     print(flow.miniflow_list)

    j = 0
    for mlx5e_miniflow_node in list_for_each_entry('struct mlx5e_miniflow_node', flow.miniflow_list.address_of_(), 'node'):
#         print(mlx5e_miniflow_node)
        print("\t%d: mlx5e_miniflow %lx" % (j, mlx5e_miniflow_node.miniflow.value_()))
        j = j + 1
