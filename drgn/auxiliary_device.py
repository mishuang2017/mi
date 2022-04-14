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
from lib import *

devs = get_mlx5_core_devs()
for i in devs.keys():
    dev = devs[i]
    pci_name = dev.device.kobj.name.string_().decode()
    if pci_name == get_pci(pf0_name):
        print(pci_name)
        print(dev.coredev_type)
        print("mlx5_core_dev %lx" % dev.address_of_())
        print("")
#         print(dev.device.kobj)
#         sd = dev.device.kobj.sd
#         print(sd)
#         for kobject in list_for_each_entry('struct kobject', dev.device.kobj.kset.list.address_of_(), 'entry'):
#             print(kobject.name)
        print(dev.device.kobj)
        sd = dev.device.kobj.sd
#         print(sd)
        for kobject in list_for_each_entry('struct kobject', dev.device.kobj.kset.list.address_of_(), 'entry'):
            name = (kobject.name.string_().decode())
            if name.find("mlx5_core") == 0:
                print(name)
#                 driver_private = container_of(kobject, "struct driver_private", "kobj")
#                 print(driver_private.driver)

#         mlx5_ib_dev = Object(prog, 'struct mlx5_ib_dev', address=dev.device.driver_data)
#         print(mlx5_ib_dev.num_ports)
