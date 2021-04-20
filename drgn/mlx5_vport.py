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
    print("mac: %02x:%02x:%02x:%02x:%02x:%02x" % (mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]))

mlx5e_priv = lib.get_mlx5_pf0()
mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
vports = mlx5_eswitch.vports
total_vports = mlx5_eswitch.total_vports
enabled_vports = mlx5_eswitch.enabled_vports

print("total_vports: %d" % total_vports)
print("enabled_vports: %d" % enabled_vports)

uplink_idx = total_vports - 1
print("vport: %x" % vports[uplink_idx].vport)
print_mac(vports[uplink_idx].info.mac)

def print_vport(vport):
    print("vport: %4x, metadata: %x" % (vport.vport, vport.metadata), end=' ')
    print_mac(vport.info.mac)

def print_devlink_port(port):
    print(port.index)

for i in range(enabled_vports):
    print_vport(vports[i])
#     print_devlink_port(vports[i].dl_port)
    print(vports[i].dl_port)

print_vport(vports[total_vports - 1])

uplink_vport = vports[1]
print_devlink_port(uplink_vport.dl_port)
# print(uplink_vport.egress.offloads.fwd_rule)
