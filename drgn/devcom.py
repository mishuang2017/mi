#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

MLX5_DEVCOM_ESW_OFFLOADS = prog['MLX5_DEVCOM_ESW_OFFLOADS']

def print_devcom_dev_list():
    print(" ==== devcom_dev_list ==== ")
    devcom_dev_list = prog['devcom_dev_list']
    for devcom in list_for_each_entry('struct mlx5_devcom_dev', devcom_dev_list.address_of_(), 'list'):
        pci_name = devcom.dev.device.kobj.name.string_().decode()
        print('--------------------------------------')
        print(pci_name)
        print(devcom)

# print_devcom_dev_list()

print(" ==== devcom_comp_list ==== ")
devcom_comp_list = prog['devcom_comp_list']
for devcom in list_for_each_entry('struct mlx5_devcom_comp', devcom_comp_list.address_of_(), 'comp_list'):
    if devcom.id != MLX5_DEVCOM_ESW_OFFLOADS:
        continue
    print(devcom.ready)
    for dev in list_for_each_entry('struct mlx5_devcom_comp_dev', devcom.comp_dev_list_head.address_of_(), 'list'):
        print(dev)
        esw = Object(prog, 'struct mlx5_eswitch', address=dev.data)
#         print(esw)
        pci_name = esw.dev.device.kobj.name.string_().decode()
        print(pci_name)
