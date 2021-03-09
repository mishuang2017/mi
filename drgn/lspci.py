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

bus_type = prog["pci_bus_type"]
subsys_private = bus_type.p
k_list = subsys_private.klist_devices.k_list

for dev in list_for_each_entry('struct device_private', k_list.address_of_(), 'knode_bus.n_node'):
    addr = dev.value_()
    device_private = Object(prog, 'struct device_private', address=addr)
    device = device_private.device

    # struct pci_dev {
    #     struct device dev;
    # }
    pci_dev = container_of(device, "struct pci_dev", "dev")

    driver_data = device.driver_data
    driver = device.driver
    if driver_data.value_():
        print(pci_dev.dev.kobj.name.string_().decode(), end='\t')
        print(driver.name.string_().decode())
