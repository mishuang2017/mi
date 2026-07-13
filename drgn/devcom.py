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
    for node in radix_tree_for_each(esw.paired.address_of_()):
        esw = Object(prog, 'struct mlx5_eswitch', address=node[1].value_())
        pci_name = esw.dev.device.kobj.name.string_().decode()
        print("paired:  %s" % pci_name)

def print_esw(devcom):
    print(" ==== devcom_comp_list ==== ")
    print("devcom.ready: %d" % devcom.ready)
#     print(devcom.key)
    print(devcom.handler)
    for dev in list_for_each_entry('struct mlx5_devcom_comp_dev', devcom.comp_dev_list_head.address_of_(), 'list'):
        print('--------------------------------------')
#         print(dev.comp.key)
#         print(dev.devc.dev)

        esw = Object(prog, 'struct mlx5_eswitch', address=dev.data)
        pci_name = esw.dev.device.kobj.name.string_().decode()
        print("primary: %s" % pci_name)
        print_esw_paired(esw)

def print_sd(devcom):
    print(" ==== devcom_comp_list ==== ")
    print("devcom.ready: %d" % devcom.ready)
    print(devcom.key)
    print(devcom.handler)
    for dev in list_for_each_entry('struct mlx5_devcom_comp_dev', devcom.comp_dev_list_head.address_of_(), 'list'):
        print('--------------------------------------')
#         print(dev.comp.key)
#         print(dev.devc.dev)

        esw = dev.devc.dev.priv.eswitch
        pci_name = esw.dev.device.kobj.name.string_().decode()
        print("primary: %s" % pci_name)
        print_esw_paired(esw)
 

devcom_comp_list = prog['devcom_comp_list']
for devcom in list_for_each_entry('struct mlx5_devcom_comp', devcom_comp_list.address_of_(), 'comp_list'):
    if devcom.id == MLX5_DEVCOM_ESW_OFFLOADS:
        print(devcom.id)
        print_esw(devcom)

#     if devcom.id == MLX5_DEVCOM_SD_GROUP:
#         print(devcom.id)
#         print_sd(devcom)
