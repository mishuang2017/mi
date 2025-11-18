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
mlxdevms = prog['mlxdevms']
# print(mlxdevms)
for node in radix_tree_for_each(mlxdevms.address_of_()):
    mlxdevm = Object(prog, 'struct mlxdevm', address=node[1].value_())
#     print(mlxdevm)
#     continue
    pci_name = mlxdevm.device.kobj.name.string_().decode()
#     if pci_name != "0000:08:00.0":
#         continue
#     print(mlxdevm.ops.eswitch_encap_mode_set)
#     print(mlxdevm.ops)

    print("========================== mlxdevm.dev.kobj.name: %s index: %d =========================" % (pci_name, mlxdevm.index))
    print("mlxdevm %x" % mlxdevm.address_of_())
#     if pci_name.find("mlx5_core.sf") == 0:
#         auxiliary_device = container_of(mlxdevm.dev, 'struct auxiliary_device', "dev")
#         print("\tauxiliary_device.name: %s" % auxiliary_device.name.string_().decode())
#         print("\tauxiliary_device.id: %d" % auxiliary_device.id)

#         print(mlxdevm.dev.driver)
#         auxiliary_driver = container_of(mlxdevm.dev.driver, "struct auxiliary_driver", "driver")
#         print(auxiliary_driver)

#         probe = auxiliary_driver.probe
#         print(address_to_name(hex(probe)))

#         remove = auxiliary_driver.remove
#         print(address_to_name(hex(remove)))

#         shutdown = auxiliary_driver.shutdown
#         print(address_to_name(hex(shutdown)))

#     print(mlxdevm._net)
#     print(mlxdevm.ops.reload_down)
#     print(mlxdevm.ops.reload_up)
#     continue
    print("\t=== mlxdevm_port start ===")

    # old kernel 
    for port in list_for_each_entry('struct mlxdevm_port', mlxdevm.port_list.address_of_(), 'list'):
#         print(port)
        print(port.type)
        print("port index: %x" % port.index)
#         if port.index & 0xffff == 0xffff:
#              print(port.attrs)

    print("\t=== mlxdevm_port end ===")

    continue
    print("=== mlxdevm.param_list ===")
    print(mlxdevm.param_list)
    for item in list_for_each_entry('struct mlxdevm_param_item', mlxdevm.param_list.address_of_(), 'list'):
        print("-------------------------------------------------------------")
        print(item)
        print(item.param.id)
        print(item.param)
