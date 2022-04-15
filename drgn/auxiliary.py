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

def print_auxiliary(driver):
    auxiliary_driver = container_of(driver, "struct auxiliary_driver", "driver")
    print(auxiliary_driver.name.string_().decode())
    print(auxiliary_driver)

def print_bus(bus):
    print("===================== %s ==========================" % bus)
    bus_type = prog[bus]
    subsys_private = bus_type.p
    k_list = subsys_private.drivers_kset

    print("=== driver ===")
    klist_drivers = subsys_private.klist_drivers
    for driver_private in list_for_each_entry('struct driver_private', klist_drivers.k_list.address_of_(), 'knode_bus.n_node'):
        print('----------------------------------')
        name = driver_private.kobj.name.string_().decode()
        print(name)
        if bus == "auxiliary_bus_type" and name.find("mlx5_core") == 0:
            print_auxiliary(driver_private.driver)
    print('')

    print("=== device ===")
    klist_devices = subsys_private.klist_devices
    for device_private in list_for_each_entry('struct device_private', klist_devices.k_list.address_of_(), 'knode_bus.n_node'):
        print(device_private.device.kobj.name.string_().decode())
    print('')

# print_bus("pci_bus_type")
print_bus("auxiliary_bus_type")

# mlx5e_rep_driver = prog['mlx5e_rep_driver']
# print(mlx5e_rep_driver)
