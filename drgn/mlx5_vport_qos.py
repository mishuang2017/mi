#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

# print esw->vports, struct mlx5_vport

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

def print_mac(mac):
    print("mac: %02x:%02x:%02x:%02x:%02x:%02x" % (mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]), end='')

def print_mlx5_vport(priv):
    mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
    vports = mlx5_eswitch.vports
    total_vports = mlx5_eswitch.total_vports
    enabled_vports = mlx5_eswitch.enabled_vports

    print("total_vports: %d" % total_vports)
    print("enabled_vports: %d" % enabled_vports)

    uplink_idx = total_vports - 1
    # uplink_vport = vports[uplink_idx]
    # print(vports)

    def print_vport(vport):
        print("mlx5_vport %x" % vport.address_of_(), end=' ')
        print("vport: %4x, metadata: %4x" % (vport.vport, vport.metadata), end=' ')
        print_mac(vport.info.mac)
        print("\tdevlink_port %18x" % vport.dl_port.value_(), end=' ')
#         if vport.dl_port:
#             print(vport.dl_port.devlink_rate)
        print("vport: %5x" % vport.vport, end=' ')
        print("enabled: %x" % vport.enabled, end=' ')
        print(vport.qos)
#         print(vport.ingress.offloads.meter_xps[0])
#         print(vport.egress.offloads.meter_xps[0])
        print('')

    # for i in range(enabled_vports):
    #     print_vport(vports[i])

    # uplink_devlink_port = mlx5e_priv.mdev.mlx5e_res.dl_port
    # print("uplink:\n\tdevlink_port %x" % uplink_devlink_port.address_of_())
    # print_vport(uplink_vport)
    # print(mlx5e_priv.mdev.mlx5e_res)

    for node in radix_tree_for_each(vports.address_of_()):
        mlx5_vport = Object(prog, 'struct mlx5_vport', address=node[1].value_())
        print_vport(mlx5_vport)

mlx5e_priv = lib.get_mlx5_pf0()
print_mlx5_vport(mlx5e_priv)
# mlx5e_priv = lib.get_mlx5_pf1()
# print_mlx5_vport(mlx5e_priv)
