#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

sys.path.append("..")
from lib import *

mlx5e_priv = get_mlx5_pf0()

# struct mlx5_esw_offload
offloads = mlx5e_priv.mdev.priv.eswitch.offloads

encap_tbl = offloads.encap_tbl

def print_udphdr(x):
    print("dest mac          : %x:%x:%x:%x:%x:%x" % (x[0], x[1], x[2], x[3], x[4], x[5]))
    print("src mac           : %x:%x:%x:%x:%x:%x" % (x[6], x[7], x[8], x[9], x[10], x[11]))
    print("ethertype         : 0x%02x%02x" % (x[12], x[13]))
    print("version|IHL       : 0x%02x" % (x[14]))
    print("DSCP|ECN          : 0x%02x" % (x[15]))
    print("total length      : 0x%02x%02x" % (x[16], x[17]))
    print("identification    : 0x%02x%02x" % (x[18], x[19]))
    print("flags|frag offset : 0x%02x%02x" % (x[20], x[21]))
    print("tme to live       : 0x%02x" % (x[22]))
    print("protocol          : 0x%02x" % (x[23]))
    print("header checksum   : 0x%02x%02x" % (x[24], x[25]))
    print("source IP address : %d.%d.%d.%d" % (x[26], x[27], x[28], x[29]))
    print("  dest IP address : %d.%d.%d.%d" % (x[30], x[31], x[32], x[33]))
    print("UDP source port   : %d" % (x[34] << 8 | x[35]))
    print("UDP dest port     : %d" % (x[36] << 8 | x[37]))
    print("UDP length        : %d" % (x[38] << 8 | x[39]))
    print("UDP checksum      : %02x%02x" % (x[40], x[41]))
    print("vxlan(VNI present): %02x%02x%02x%02x" % (x[42], x[43], x[44], x[45]))
    print("vxlan(VNI)        : %d" % (x[46] << 16 | x[47] << 8 | x[48]))
    print("vxlan(reserved)   : %d" % (x[49]))

def print_mlx5e_encap_entry(e):
#     print(e)
    print(e.encap_header)
    x = Object(prog, 'unsigned char *', address=e.encap_header.address_of_())
    print_udphdr(x)
    print("encap_size: %d" % e.encap_size)
#     for i in range(e.encap_size):
#         print("%#x " % e.encap_header[i])
    print("mlx5e_encap_entry %lx" % e.value_())
    print(e.m_neigh)
    print_tun(e.tun_info)
    print("encap_id %lx" % e.encap_id.value_())

# for i in range(256):
#     node = encap_tbl[i].first
#     while node.value_():
#         mlx5e_encap_entry = container_of(node, "struct mlx5e_encap_entry", "encap_hlist")
#         print_mlx5e_encap_entry(mlx5e_encap_entry)
#         node = node.next

mlx5e_rep_priv = get_mlx5e_rep_priv()
addr = mlx5e_rep_priv.neigh_update.neigh_list.address_of_()
for nhe in list_for_each_entry('struct mlx5e_neigh_hash_entry', addr, 'neigh_list'):
#     print(nhe)
    print("mlx5e_neigh_hash_entry %lx" % nhe.value_())
    for e in list_for_each_entry('struct mlx5e_encap_entry', nhe.encap_list.address_of_(), 'encap_list'):
        print_mlx5e_encap_entry(e)
