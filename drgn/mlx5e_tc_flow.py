#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

print_mlx5e_tc_flow_flags()

for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    addr = dev.value_()
    if "enp" not in name:
        continue;

    mlx5e_priv_addr = addr + prog.type('struct net_device').size
    mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)

    ppriv = mlx5e_priv.ppriv
    if ppriv.value_() == 0:
        continue

#     print(name)
#     print(dev.name)
    mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())
    tc_ht = mlx5e_rep_priv.tc_ht

    for i, flow in enumerate(hash(tc_ht, 'struct mlx5e_tc_flow', 'node')):
#         print(flow.attr.esw_attr[0])
        print(" --- %d ---" % (i + 1))
        print_mlx5e_tc_flow(flow)

#         MLX5E_TC_FLOW_FLAG_INGRESS               = MLX5E_TC_FLAG_INGRESS_BIT,
#         MLX5E_TC_FLOW_FLAG_EGRESS                = MLX5E_TC_FLAG_EGRESS_BIT,
#         MLX5E_TC_FLOW_FLAG_ESWITCH               = MLX5E_TC_FLAG_ESW_OFFLOAD_BIT,
#         MLX5E_TC_FLOW_FLAG_FT                    = MLX5E_TC_FLAG_FT_OFFLOAD_BIT,
#         MLX5E_TC_FLOW_FLAG_NIC                   = MLX5E_TC_FLAG_NIC_OFFLOAD_BIT,
#         MLX5E_TC_FLOW_FLAG_OFFLOADED             = MLX5E_TC_FLOW_BASE,
#         MLX5E_TC_FLOW_FLAG_HAIRPIN               = MLX5E_TC_FLOW_BASE + 1,
#         MLX5E_TC_FLOW_FLAG_HAIRPIN_RSS           = MLX5E_TC_FLOW_BASE + 2,
#         MLX5E_TC_FLOW_FLAG_SLOW                  = MLX5E_TC_FLOW_BASE + 3,
#         MLX5E_TC_FLOW_FLAG_DUP                   = MLX5E_TC_FLOW_BASE + 4,
#         MLX5E_TC_FLOW_FLAG_NOT_READY             = MLX5E_TC_FLOW_BASE + 5,
#         MLX5E_TC_FLOW_FLAG_DELETED               = MLX5E_TC_FLOW_BASE + 6,
#         MLX5E_TC_FLOW_FLAG_CT                    = MLX5E_TC_FLOW_BASE + 7,
#         MLX5E_TC_FLOW_FLAG_L3_TO_L2_DECAP        = MLX5E_TC_FLOW_BASE + 8,
#         MLX5E_TC_FLOW_FLAG_TUN_RX                = MLX5E_TC_FLOW_BASE + 9,
#         MLX5E_TC_FLOW_FLAG_FAILED                = MLX5E_TC_FLOW_BASE + 10,
#         MLX5E_TC_FLOW_FLAG_SAMPLE                = MLX5E_TC_FLOW_BASE + 11,

print("MLX5E_TC_FLOW_FLAG_INGRESS        %10x" % (prog['MLX5E_TC_FLOW_FLAG_INGRESS'].value_()))
print("MLX5E_TC_FLOW_FLAG_EGRESS         %10x" % (prog['MLX5E_TC_FLOW_FLAG_EGRESS'].value_()))
print("MLX5E_TC_FLOW_FLAG_NIC            %10x" % (prog['MLX5E_TC_FLOW_FLAG_NIC'].value_()))
print("MLX5E_TC_FLOW_FLAG_ESWITCH        %10x" % (prog['MLX5E_TC_FLOW_FLAG_ESWITCH'].value_()))
print('')
print("MLX5E_TC_FLOW_FLAG_FT             %10x" % (prog['MLX5E_TC_FLOW_FLAG_FT'].value_()))
print("MLX5E_TC_FLOW_FLAG_OFFLOADED      %10x" % (prog['MLX5E_TC_FLOW_FLAG_OFFLOADED'].value_()))
print("MLX5E_TC_FLOW_FLAG_HAIRPIN        %10x" % (prog['MLX5E_TC_FLOW_FLAG_HAIRPIN'].value_()))
print("MLX5E_TC_FLOW_FLAG_HAIRPIN_RSS    %10x" % (prog['MLX5E_TC_FLOW_FLAG_HAIRPIN_RSS'].value_()))
print('')
print("MLX5E_TC_FLOW_FLAG_SLOW           %10x" % (prog['MLX5E_TC_FLOW_FLAG_SLOW'].value_()))
print("MLX5E_TC_FLOW_FLAG_DUP            %10x" % (prog['MLX5E_TC_FLOW_FLAG_DUP'].value_()))
print("MLX5E_TC_FLOW_FLAG_NOT_READY      %10x" % (prog['MLX5E_TC_FLOW_FLAG_NOT_READY'].value_()))
print("MLX5E_TC_FLOW_FLAG_DELETED        %10x" % (prog['MLX5E_TC_FLOW_FLAG_DELETED'].value_()))
print('')
print("MLX5E_TC_FLOW_FLAG_CT             %10x" % (prog['MLX5E_TC_FLOW_FLAG_CT'].value_()))
print("MLX5E_TC_FLOW_FLAG_L3_TO_L2_DECAP %10x" % (prog['MLX5E_TC_FLOW_FLAG_L3_TO_L2_DECAP'].value_()))
print("MLX5E_TC_FLOW_FLAG_TUN_RX         %10x" % (prog['MLX5E_TC_FLOW_FLAG_TUN_RX'].value_()))
print("MLX5E_TC_FLOW_FLAG_FAILED         %10x" % (prog['MLX5E_TC_FLOW_FLAG_FAILED'].value_()))
print('')
print("MLX5E_TC_FLOW_FLAG_SAMPLE         %10x" % (prog['MLX5E_TC_FLOW_FLAG_SAMPLE'].value_()))
