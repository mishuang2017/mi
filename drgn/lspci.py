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

devs = {}

subsys_private = get_subsys_private("pci")
k_list = subsys_private.klist_devices.k_list

for dev in list_for_each_entry('struct device_private', k_list.address_of_(), 'knode_bus.n_node'):
    addr = dev.value_()
    device_private = Object(prog, 'struct device_private', address=addr)
    device = device_private.device

    # struct pci_dev {
    #     struct device dev;
    # }

    driver_data = device.driver_data
    if driver_data.value_():

        pci_dev = container_of(device, "struct pci_dev", "dev")
        for i in range(6):
            print(pci_dev.res_attr_wc[i])
        print(pci_dev.dev.kobj.name.string_().decode(), end='\t')

        driver = device.driver
        print(driver.name.string_().decode())
    else:
        print("driver_data is NULL")

    pci_dev = container_of(device, "struct pci_dev", "dev")
    print(pci_dev.is_physfn)
    print(pci_dev.is_virtfn)
    print("enable_cnt           %x" % pci_dev.enable_cnt.counter)
    print("pci_dev              %x" % pci_dev)
    print("pci_dev.physfn       %x" % pci_dev.physfn)
    if pci_dev.is_virtfn:
        print("pci_dev.physfn.sriov %x" % pci_dev.physfn.sriov)
#         print(pci_dev.physfn.sriov)
    else:
        print("pci_dev.sriov")
        print(pci_dev.sriov)
    print("")

#     print("pci_dev.is_virtfn: %d" % pci_dev.is_virtfn)
