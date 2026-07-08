#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os
import drgn

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *
# import lib

DEVLINK_RATE_TYPE_LEAF = prog['DEVLINK_RATE_TYPE_LEAF']
DEVLINK_RATE_TYPE_NODE = prog['DEVLINK_RATE_TYPE_NODE']

# prog = drgn.program_from_core_dump("/var/crash/vmcore.4")
# prog = drgn.program_from_kernel()
devlinks = prog['devlinks']
# print(devlinks)
for node in radix_tree_for_each(devlinks.address_of_()):
    devlink = Object(prog, 'struct devlink', address=node[1].value_())
    if not devlink.dev and devlink.index != 0:
        print("\n=== devlink_rate list for index %d ===\n" % devlink.index)
        for devlink_rate in list_for_each_entry('struct devlink_rate', devlink.rate_list.address_of_(), 'list'):
            print("=======================================================")
            devlink_rate_devlink = devlink_rate.devlink
            pci_name = devlink_rate_devlink.dev.kobj.name.string_().decode()
            print(devlink_rate.name)
            print(devlink_rate.type)
            print(pci_name)
            if devlink_rate.type == DEVLINK_RATE_TYPE_NODE:
                mlx5_esw_sched_node = cast("struct mlx5_esw_sched_node *", devlink_rate.priv)
                print("mlx5_esw_sched_node: %x" % mlx5_esw_sched_node)
            elif devlink_rate.type == DEVLINK_RATE_TYPE_LEAF:
                mlx5_vport = cast("struct mlx5_vport *", devlink_rate.priv)
                print("mlx5_vport.vport: %d" % mlx5_vport.vport)
            if devlink_rate.parent:
                print(devlink_rate.parent)
        continue

    pci_name = devlink.dev.kobj.name.string_().decode()
    print("devlink.dev.kobj.name: %s" % pci_name)
    if pci_name.find("mlx5_core.sf") == 0:
        auxiliary_device = container_of(devlink.dev, 'struct auxiliary_device', "dev")
        print("\tauxiliary_device.name: %s" % auxiliary_device.name.string_().decode())
        print("\tauxiliary_device.id: %d" % auxiliary_device.id)

#         print(devlink.dev.driver)
        auxiliary_driver = container_of(devlink.dev.driver, "struct auxiliary_driver", "driver")
#         print(auxiliary_driver)

        probe = auxiliary_driver.probe
        print(address_to_name(hex(probe)))

        remove = auxiliary_driver.remove
        print(address_to_name(hex(remove)))

        shutdown = auxiliary_driver.shutdown
        print(address_to_name(hex(shutdown)))

    mlx5_core_dev = Object(prog, 'struct mlx5_core_dev', address=devlink.priv.address_of_().value_())
    print("mlx5_core_dev %x" % mlx5_core_dev.address_of_())
    print("=== devlink_port ===")
    for node in radix_tree_for_each(devlink.ports.address_of_()):
        port = Object(prog, 'struct devlink_port', address=node[1].value_())
        print("port.index: %x" % port.index)
        if not port.devlink_rate or not port.switch_port:
            continue
        if port.devlink_rate.type == DEVLINK_RATE_TYPE_LEAF:
            print(port.devlink_rate.name)
            mlx5_vport = cast("struct mlx5_vport *", port.devlink_rate.priv)
            print("mlx5_vport.vport: %d" % mlx5_vport.vport)
#             print(port.devlink_rate)
#             if port.devlink_rate.parent:
#                 print(port.devlink_rate.parent)
