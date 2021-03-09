#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

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


for i in range(enabled_vports):
    vport = vports[i]
    print("vport: %x, metadata: %x" % (vport.vport, vport.metadata), end=' ')
    print_mac(vport.info.mac)
