#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

# mlx5_esw_offloads_devcom_init
# mlx5_lag_register_hca_devcom_comp

MLX5_DEVCOM_ESW_OFFLOADS = prog['MLX5_DEVCOM_ESW_OFFLOADS']
MLX5_DEVCOM_SD_GROUP = prog['MLX5_DEVCOM_SD_GROUP']

def bswap32(x):
    x &= 0xffffffff
    return ((x & 0xff) << 24) | ((x & 0xff00) << 8) | ((x >> 8) & 0xff00) | ((x >> 24) & 0xff)

def dev_vhca_id(mdev):
    # MLX5_CAP_GEN(mdev, vhca_id): cmd_hca_cap dword1 low 16 bits (big-endian)
    try:
        return bswap32(int(mdev.caps.hca[0].cur[1].value_())) & 0xffff
    except Exception as e:
        return -1

def print_devcom_dev_list():
    print(" ==== devcom_dev_list ==== ")
    devcom_dev_list = prog['devcom_dev_list']
    for devcom in list_for_each_entry('struct mlx5_devcom_dev', devcom_dev_list.address_of_(), 'list'):
        pci_name = devcom.dev.device.kobj.name.string_().decode()
        print('--------------------------------------')
        print(pci_name)
        print(devcom)

# print_devcom_dev_list()
# exit(0)

def print_esw_paired(esw):
    # esw->paired is an xarray keyed by the PEER vhca_id -> the index IS the vhca_id
    for index, entry in radix_tree_for_each(esw.paired.address_of_()):
        pe = Object(prog, 'struct mlx5_eswitch', address=entry.value_())
        pci_name = pe.dev.device.kobj.name.string_().decode()
        print("    paired: %s  vhca_id=%d" % (pci_name, index))

def print_esw(devcom):
    print(" ==== devcom_comp_list ==== ")
    print("comp id=%s  key=0x%x  flags=0x%x  ready=%d" % (
        str(devcom.id),
        int(devcom.key.key.val.value_()),
        int(devcom.key.flags.value_()),
        int(devcom.ready.value_())))
    print(devcom.handler)
    for dev in list_for_each_entry('struct mlx5_devcom_comp_dev', devcom.comp_dev_list_head.address_of_(), 'list'):
        print('--------------------------------------')
#         print(dev.comp.key)
#         print(dev.devc.dev)

        esw = Object(prog, 'struct mlx5_eswitch', address=dev.data)
        pci_name = esw.dev.device.kobj.name.string_().decode()
        print("primary: %s  vhca_id=%d  num_peers=%d" %
              (pci_name, dev_vhca_id(esw.dev), int(esw.num_peers.value_())))
        print_esw_paired(esw)

def print_sd(devcom):
    print(" ==== devcom_comp_list ==== ")
    print("devcom.ready: %d" % int(devcom.ready.value_()))
    print(devcom.key)
    print(devcom.handler)
    print('=== devcom.comp_dev_list_head ===')
    for dev in list_for_each_entry('struct mlx5_devcom_comp_dev', devcom.comp_dev_list_head.address_of_(), 'list'):
        print('------------')
#         print(dev.comp.key)
#         print(dev.devc.dev)

        esw = dev.devc.dev.priv.eswitch
        pci_name = esw.dev.device.kobj.name.string_().decode()
        print("%s" % pci_name)

devcom_comp_list = prog['devcom_comp_list']
for devcom in list_for_each_entry('struct mlx5_devcom_comp', devcom_comp_list.address_of_(), 'comp_list'):
    if devcom.id == MLX5_DEVCOM_ESW_OFFLOADS:
        print(devcom.id)
        print_esw(devcom)

#     if devcom.id == MLX5_DEVCOM_SD_GROUP:
#         print(devcom.id)
#         print_sd(devcom)
#         print(devcom)
