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

mlx5e_priv = lib.get_mlx5_pf0()
mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
vports = mlx5_eswitch.vports
total_vports = mlx5_eswitch.total_vports
enabled_vports = mlx5_eswitch.enabled_vports

print("total_vports: %d" % total_vports)
print("enabled_vports: %d" % enabled_vports)

uplink_idx = total_vports - 1
uplink_vport = vports[uplink_idx]

def print_vport(vport):
    print("mlx5_vport %x" % vport.address_of_(), end=' ')
    print("vport: %4x, metadata: %4x" % (vport.vport, vport.metadata), end=' ')
    print_mac(vport.info.mac)
    print("\tdevlink_port %18x" % vport.dl_port.value_(), end=' ')
    print("vport: %5x" % vport.vport, end=' ')
    print("enabled: %x" % vport.enabled, end=' ')
    print('')

for i in range(enabled_vports):
    print_vport(vports[i])

uplink_devlink_port = mlx5e_priv.mdev.mlx5e_res.dl_port
print("uplink:\n\tdevlink_port %x" % uplink_devlink_port.address_of_())
print_vport(uplink_vport)
# print(mlx5e_priv.mdev.mlx5e_res)
