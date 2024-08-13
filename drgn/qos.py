#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5e_priv(pf0_name)
esw = mlx5e_priv.mdev.priv.eswitch

if esw.qos.refcnt.refs.counter == 0:
    print("qos is not enabled")
    exit()

print("\n === esw qos ===\n")
print(esw.qos)
mlx5_esw_rate_group = esw.qos.group0

# print("\n === esw.qos.group0 ===\n")
# print(mlx5_esw_rate_group)


# print("\n === mlx5_esw_rate_group ===\n")
# for group in list_for_each_entry('struct mlx5_esw_rate_group', \
#     mlx5_esw_rate_group.list.address_of_(), 'list'):
#     print(group)
 
print("\n === groups ===\n")
for group in list_for_each_entry('struct mlx5_esw_rate_group', \
    esw.qos.groups.address_of_(), 'list'):
    print(group)

def print_mac(mac):
    print("mac: %02x:%02x:%02x:%02x:%02x:%02x" % (mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]), end='')

print("\n === vports qos ===\n")

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
        group = vport.qos.group
        if group.value_() == 0:
            return
        print("mlx5_vport %x" % vport.address_of_(), end=' ')
        print("vport: %4x, %4d, metadata: %4x" % (vport.vport, vport.vport, vport.metadata), end=' ')
        print_mac(vport.info.mac)
        print("\tdevlink_port %18x" % vport.dl_port.value_(), end=' ')
        print("vport: %5x" % vport.vport, end=' ')
        print("enabled: %x" % vport.enabled.value_(), end=' ')
        print(vport.qos)
        print('')

    for node in radix_tree_for_each(vports.address_of_()):
        mlx5_vport = Object(prog, 'struct mlx5_vport', address=node[1].value_())
#         if mlx5_vport.vport < 4:
        print_vport(mlx5_vport)

mlx5e_priv = get_mlx5_pf0()
print_mlx5_vport(mlx5e_priv)
