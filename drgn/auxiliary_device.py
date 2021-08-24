#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

devs = lib.get_mlx5_core_devs()
for i in devs.keys():
    dev = devs[i]
    pci_name = dev.device.kobj.name.string_().decode()
    print(pci_name)
    print(dev.coredev_type)
    print("mlx5_core_dev %lx" % dev.address_of_())
    print("")
#     print(dev.device)
    mlx5_ib_dev = Object(prog, 'struct mlx5_ib_dev', address=dev.device.driver_data)
    print(mlx5_ib_dev.num_ports)
