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

devs = {}


# bus_type = prog["pci_bus_type"]
# subsys_private = bus_type.p
# k_list = subsys_private.drivers_kset

# for kobject in list_for_each_entry('struct kobject', k_list.list.address_of_(), 'entry'):
#     print(kobject)

# klist_drivers = subsys_private.klist_drivers
# for driver_private in list_for_each_entry('struct driver_private', klist_drivers.k_list.address_of_(), 'knode_bus.n_node'):
#     name = driver_private.kobj.name.string_().decode()
#     if name.find("mlx5_core") == 0:
#         print(driver_private)
#         auxiliary_driver = container_of(driver_private.driver, "struct auxiliary_driver", "driver")
#         print(auxiliary_driver)

bus_type = prog["auxiliary_bus_type"]
subsys_private = bus_type.p
k_list = subsys_private.drivers_kset

# for kobject in list_for_each_entry('struct kobject', k_list.list.address_of_(), 'entry'):
#     print(kobject)

klist_drivers = subsys_private.klist_drivers
for driver_private in list_for_each_entry('struct driver_private', klist_drivers.k_list.address_of_(), 'knode_bus.n_node'):
    name = driver_private.kobj.name.string_().decode()
    if name.find("mlx5_core") == 0:
#         print(driver_private.driver)
        auxiliary_driver = container_of(driver_private.driver, "struct auxiliary_driver", "driver")
        print(auxiliary_driver)

# mlx5e_rep_driver = prog['mlx5e_rep_driver']
# print(mlx5e_rep_driver)
