#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
import time
import sys
import os

# print esw->vports, struct mlx5_vport

sys.path.append(".")
from lib_pedit import *

def print_mac(mac):
    print("mac: %02x:%02x:%02x:%02x:%02x:%02x" % (mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]), end='')

def print_esw_mc_table(table):
    for i in range(256):
        node = table[i].first
        while node.value_():
            obj = container_of(node, "struct esw_mc_addr", "node.hlist")
            addr = Object(prog, 'struct esw_mc_addr', address=obj.value_())
#             print(addr)
            mac = addr.node.addr
            print_mac(mac)
            print("\trefcnt: %d" % addr.refcnt.value_())
            print_mlx5_flow_handle(addr.uplink_rule)
            node = node.next

def print_mc_list(list):
    for i in range(256):
        node = list[i].first
        while node.value_():
            obj = container_of(node, "struct vport_addr", "node.hlist")
            addr = Object(prog, 'struct vport_addr', address=obj.value_())
#             print(addr)
            mac = addr.node.addr
            print_mac(mac)
            print("\t addr.mc_promisc %d" % addr.mc_promisc.value_())
            node = node.next

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
        print("vport: %4x, metadata: %4x, trusted: %d" % (vport.vport, vport.metadata, vport.info.trusted), end=' ')
        print_mac(vport.info.mac)
        print("\tdevlink_port %18x" % vport.dl_port.value_(), end=' ')
        print("enabled: %x" % vport.enabled.value_(), end=' ')
        print("vlan: %d" % vport.info.vlan, end=' ')
        if vport.enabled.value_():
            print('\n-----mc---------')
            print_mc_list(vport.mc_list)
            print('-----uc---------')
            print_mc_list(vport.uc_list)
            if vport.allmulti_rule:
                print('-----vport.allmulti_rule---------')
                print_mlx5_flow_handle(vport.allmulti_rule)
            if vport.promisc_rule:
                print('-----vport.promisc_rule---------')
                print_mlx5_flow_handle(vport.promisc_rule)
        print('')

    for node in radix_tree_for_each(vports.address_of_()):
        mlx5_vport = Object(prog, 'struct mlx5_vport', address=node[1].value_())
        print_vport(mlx5_vport)

mlx5e_priv = get_mlx5_pf0()
print_mlx5_vport(mlx5e_priv)

print("\n=============mlx5_eswitch.mc_table==================\n")
mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
print_esw_mc_table(mlx5_eswitch.mc_table)

# mlx5e_priv = get_mlx5_pf1()
# print_mlx5_vport(mlx5e_priv)
