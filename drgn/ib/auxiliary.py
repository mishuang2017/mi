#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object
import time
import socket
import sys
import os

sys.path.append("..")
from lib import *

def print_auxiliary_driver(driver):
    auxiliary_driver = container_of(driver, "struct auxiliary_driver", "driver")
    print(auxiliary_driver.name.string_().decode())
    print(auxiliary_driver)

def print_auxiliary_device(device):
    auxiliary_device = container_of(device, "struct auxiliary_device", "dev")
#     print(auxiliary_device.id)
    driver_data = auxiliary_device.dev.driver_data
    print("driver_data %x" % driver_data)
    mlx5_ib_dev = Object(prog, 'struct mlx5_ib_dev', address=driver_data)
    print(mlx5_ib_dev.ib_dev.ops)

    mlx5_adev = container_of(auxiliary_device, "struct mlx5_adev", "adev")
#     print(mlx5_adev)
#     print("%x" % mlx5_adev.idx)
#     print("%x" % mlx5_adev.mdev)
    print("mlx5_core_dev device name: %-20s" % mlx5_adev.mdev.device.kobj.name.string_().decode())
    print('')

def print_bus(bus):
    print("===================== %s ==========================" % bus)
    subsys_private = get_subsys_private(bus)
    k_list = subsys_private.drivers_kset

    print("=== driver ===")
    klist_drivers = subsys_private.klist_drivers
    for driver_private in list_for_each_entry('struct driver_private', klist_drivers.k_list.address_of_(), 'knode_bus.n_node'):
        print('----------------------------------')
        name = driver_private.kobj.name.string_().decode()
        print(name)
        if bus == "auxiliary" and name.find("mlx5_core") == 0:
            print_auxiliary_driver(driver_private.driver)
    print('')

    print("=== device ===")
    klist_devices = subsys_private.klist_devices
    for device_private in list_for_each_entry('struct device_private', klist_devices.k_list.address_of_(), 'knode_bus.n_node'):
        print("auxiliary device name:     %-20s, %x" % (device_private.device.kobj.name.string_().decode(), device_private.device))
        if "mlx5_core.rdma.0" == device_private.device.kobj.name.string_().decode():
            print_auxiliary_device(device_private.device)
    print('')

# print_bus("pci_bus_type")
print_bus("auxiliary")

# mlx5e_rep_driver = prog['mlx5e_rep_driver']
# print(mlx5e_rep_driver)
