#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
import time
import socket
import sys
import os
import drgn

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *
# import lib

# prog = drgn.program_from_core_dump("/var/crash/vmcore.4")
# prog = drgn.program_from_kernel()
devlinks = prog['devlinks']
# print(devlinks)
for node in radix_tree_for_each(devlinks.address_of_()):
    devlink = Object(prog, 'struct devlink', address=node[1].value_())
    pci_name = devlink.dev.kobj.name.string_().decode()
#     if pci_name != "0000:08:00.0":
#         continue
    print(devlink.ops.port_new)
    print(devlink.ops.port_del)
    print(devlink.ops.reload_down)
    print(devlink.ops.reload_up)
#     print(devlink.ops.port_function_hw_addr_get)

    print("========================== devlink.dev.kobj.name: %s index: %d =========================" % (pci_name, devlink.index))
    print("devlink %x" % devlink.address_of_())
    print("devlink.features: %x" % devlink.features)
#     if pci_name.find("mlx5_core.sf") == 0:
#         auxiliary_device = container_of(devlink.dev, 'struct auxiliary_device', "dev")
#         print("\tauxiliary_device.name: %s" % auxiliary_device.name.string_().decode())
#         print("\tauxiliary_device.id: %d" % auxiliary_device.id)

#         print(devlink.dev.driver)
#         auxiliary_driver = container_of(devlink.dev.driver, "struct auxiliary_driver", "driver")
#         print(auxiliary_driver)

#         probe = auxiliary_driver.probe
#         print(address_to_name(hex(probe)))

#         remove = auxiliary_driver.remove
#         print(address_to_name(hex(remove)))

#         shutdown = auxiliary_driver.shutdown
#         print(address_to_name(hex(shutdown)))

#     print(devlink._net)
#     print(devlink.ops.reload_down)
#     print(devlink.ops.reload_up)
    mlx5_core_dev = Object(prog, 'struct mlx5_core_dev', address=devlink.priv.address_of_().value_())
    print("mlx5_core_dev %x" % mlx5_core_dev.address_of_())
    print("mlx5_priv %x" % mlx5_core_dev.priv.address_of_())
    print("mlx5_eswitch %x" % mlx5_core_dev.priv.eswitch)
    print("mlx5_core_dev.coredev_type: ")
    print(mlx5_core_dev.coredev_type)
#     continue
    print("\t=== devlink_port ===")

    # old kernel 
    for port in list_for_each_entry('struct devlink_port', devlink.port_list.address_of_(), 'list'):
        print('\t-------------------------')
        print("\tdevlink_port.switch_port: %d" % port.switch_port)
        print("\tport index: %x" % port.index)
#         print(port.type)
        mlx5_devlink_port = container_of(port, "struct mlx5_devlink_port", "dl_port")
#         print(mlx5_devlink_port.vport.vport)
        netdev = Object(prog, 'struct net_device', address=port.type_dev)
        print("\tnetdev.name: %s" % netdev.name)
#         print("\n\tport index: %x" % port.index)
#         if port.index & 0xffff == 0xffff:
#              print(port.attrs)

    continue
#     for node in radix_tree_for_each(devlink.params.address_of_()):
#         print(node)
#         param = Object(prog, 'struct devlink_param_item', address=node[1].value_())
#         if param.driverinit_value_valid:
#             print(param)
#             print(param.param.name)
    print("=== devlink.param_list ===")
#     print(devlink.param_list)
    for item in list_for_each_entry('struct devlink_param_item', devlink.param_list.address_of_(), 'list'):
#         print("-------------------------------------------------------------")
        print(item)
#         print(item.param)
#         print(item.param.name)
#         print(item.param.id)
