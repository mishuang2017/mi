#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

esw_manager_vport = 0

MLX5_NUM_TT = prog['MLX5_NUM_TT']

def print_port_sel(port_sel):
    print(port_sel)

    print('------port_sel start-------')
    mlx5_lag_definer = port_sel.outer.definers
    for i in range(MLX5_NUM_TT.value_()):
        if mlx5_lag_definer[i]:
            print("---------------------%d-----------------------\n" % i)
            print(mlx5_lag_definer[i].definer)
            flow_table("", mlx5_lag_definer[i].ft)
    print('------port_sel end-------')

# for name in pf0_name,pf1_name:
for name in pf0_name,:
    mlx5e_priv = get_mlx5e_priv(name)
    mlx5_lag = mlx5e_priv.mdev.priv.lag

    print(mlx5_lag)

    print('-------------')
    MLX5_LAG_MODE_ROCE = prog['MLX5_LAG_MODE_ROCE']
    MLX5_LAG_MODE_SRIOV = prog['MLX5_LAG_MODE_SRIOV']
    MLX5_LAG_MODE_MULTIPATH = prog['MLX5_LAG_MODE_MULTIPATH']

    print("MLX5_LAG_MODE_ROCE: %x" % MLX5_LAG_MODE_ROCE)
    print("MLX5_LAG_MODE_SRIOV: %x" % MLX5_LAG_MODE_SRIOV)
    print("MLX5_LAG_MODE_MULTIPATH: %x" % MLX5_LAG_MODE_MULTIPATH)

    print("mlx5_lag.mode_flags: %d" % mlx5_lag.mode_flags)
    print('-------------')
#     print("mode_flags: %x (MLX5_LAG_MODE_FLAG_SHARED_FDB: 2)" % mlx5_lag.mode_flags)
#     print("state_flags: %x (MLX5_LAG_MODE_NDEVS_READY = 1)" % mlx5_lag.state_flags)
#     print(mlx5_lag)
#     print(mlx5_lag.v2p_map)
#     print(mlx5_lag.tracker)
    port_sel = mlx5_lag.port_sel
    print_port_sel(port_sel)
#     continue
    print(mlx5_lag.pf[0])
    print(mlx5_lag.pf[1])
    print("mlx5_lag.ports: %d" % mlx5_lag.ports)
    print(mlx5_lag.mode)
#     print("mlx5_lag %x, flags: %x" % (mlx5_lag, mlx5_lag.flags))
#     print_fib_info(mlx5_lag.lag_mp.mfi)
    print('')
    esw = mlx5e_priv.mdev.priv.eswitch
    esw_manager_vport = esw.manager_vport
#     print("esw.manager_vport: %x" % esw_manager_vport)

# exit(0)

# if mlx5_lag.mode !=  MLX5_LAG_MODE_SRIOV:
#     exit(0)

def print_mlx5_vport(priv):
    mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
    vports = mlx5_eswitch.vports
    total_vports = mlx5_eswitch.total_vports
    enabled_vports = mlx5_eswitch.enabled_vports

    print("total_vports: %d" % total_vports)
    print("enabled_vports: %d" % enabled_vports)

    def print_vport(vport):
        if vport.vport != esw_manager_vport and vport.vport != 0xffff:
            return
        print(" ==== %s %x ====\n" % (priv.netdev.name.string_().decode(), vport.vport))
        print("mlx5_vport %x" % vport.address_of_(), end=' ')
        print("vport: %4x, metadata: %4x" % (vport.vport, vport.metadata), end=' ')
        print("\tdevlink_port %18x" % vport.dl_port.value_(), end=' ')
        print("vport: %5x" % vport.vport, end=' ')
        print("enabled: %x" % vport.enabled.value_(), end=' ')
        print('')

        # if egress acl is not NULL, it is shared_fdb
        if vport.egress.acl:
            flow_table("vport.egress.acl", vport.egress.acl)

        print("vport.ingress.acl start")
        if vport.ingress.acl:
            flow_table("vport.ingress.acl", vport.ingress.acl)
        print("vport.ingress.acl end")

    for node in radix_tree_for_each(vports.address_of_()):
        mlx5_vport = Object(prog, 'struct mlx5_vport', address=node[1].value_())
#         print_vport(mlx5_vport)

mlx5e_priv = get_mlx5_pf0()
print_mlx5_vport(mlx5e_priv)

# mlx5e_priv = get_mlx5_pf1()
# print_mlx5_vport(mlx5e_priv)
