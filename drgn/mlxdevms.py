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
    mlx5_devm_device = container_of(mlxdevm.address_of_(), "struct mlx5_devm_device", "device")
    if mlx5_devm_device.dev.coredev_type == prog['MLX5_COREDEV_VF']:
        continue
#     print(mlxdevm)
    print("========================== mlxdevm.dev.kobj.name: %s index: %d =========================" % (pci_name, mlxdevm.index))
    print("mlxdevm %x" % mlxdevm.address_of_())
    if mlxdevm.dev_name_index.value_():
        print("mlxdevm.dev_name_index: %s" % mlxdevm.dev_name_index)
        try:
            print("pci_name: %s" % mlxdevm.dev.kobj.name.string_().decode())
        except drgn.FaultError:
            print("pci_name: <not mapped>")
        for rate in list_for_each_entry('struct mlxdevm_rate', mlxdevm.rate_list.address_of_(), 'list'):
            print("\tmlxdevm_rate %x" % rate.list.address_of_().value_())
            print("\t\ttype: %s" % rate.type.format_())
            rate_mlxdevm = rate.mlxdevm
            try:
                rate_pci_name = rate_mlxdevm.dev.kobj.name.string_().decode()
            except drgn.FaultError:
                rate_pci_name = "<not mapped>"
            print("\t\tmlxdevm: %x (%s)" % (rate_mlxdevm.value_(), rate_pci_name))
            print("\t\ttx_share: %d, tx_max: %d" % (rate.tx_share, rate.tx_max))
            if rate.type == prog['MLXDEVM_RATE_TYPE_NODE']:
                print("\t\tname: %s" % rate.name.string_().decode())
            if rate.parent:
                print("\t\tparent: %s" % rate.parent.name.string_().decode())
            else:
                print("\t\tparent: none")
        continue
    pci_name = mlxdevm.dev.kobj.name.string_().decode()
#     if pci_name != "0000:08:00.0":
#         continue
#     print(mlxdevm.ops.eswitch_encap_mode_set)
#     print(mlxdevm.ops)


#     print(mlxdevm.dev_driver)
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
    mlx5_core_dev = mlx5_devm_device.dev
    print("mlx5_core_dev %x" % mlx5_core_dev.value_())
    print("mlx5_priv %x" % mlx5_core_dev.priv.address_of_())
#     print(mlx5_core_dev.priv.fw_reset)
    print("mlx5_eswitch %x" % mlx5_core_dev.priv.eswitch)
    print("mlx5_core_dev.coredev_type: ")
    print(mlx5_core_dev.coredev_type)
#     continue
    print("\t=== mlxdevm_port start ===")

    # new kernel
    for node in radix_tree_for_each(mlxdevm.ports.address_of_()):
        port = Object(prog, 'struct mlxdevm_port', address=node[1].value_())
#         if port.index != 1:
#             continue
        print("\tmlxdevm_port %x" % node[1].value_())
#         print(port.mlxdevm_rate)
#         print(port.mlxdevm_rate.parent)
#         print(port.dl_port)
        print("\tport index: %x, %d" % (port.index, port.index))
#         print(port.ops.port_fn_hw_addr_get)
#         print(port.switch_port)
#         print(port.type_eth.ifname);
#         for i in range(port.attrs.switch_id.id_len):
#             print("%02x:" % port.attrs.switch_id.id[i], end="")
        print("")

    print("\t=== mlxdevm_port end ===")
    mlx5_devm_device = container_of(mlxdevm.address_of_(), "struct mlx5_devm_device", "device")
#     print(mlx5_devm_device)
    devm_sfs = mlx5_devm_device.devm_sfs
    print("\t=== devm_sfs start ===")
    for node in radix_tree_for_each(devm_sfs.address_of_()):
        print("\tsf port index: %#x, %d" % (node[0], node[0]))
#         port = Object(prog, 'void *', address=node[1].value_())
#         print(*port)
#         print(port)
#         print("port: %x" % port)
    print("\t=== devm_sfs end ===")

    print("\t=== mlxdevm_rate start ===")
#     for rate in list_for_each_entry('struct mlxdevm_rate', mlxdevm.rate_list.address_of_(), 'list'):
#         print(rate)
    print("\t=== mlxdevm_rate end ===")

    # old kernel 
#     for port in list_for_each_entry('struct mlxdevm_port', mlxdevm.port_list.address_of_(), 'list'):
#         print(port)
#         print(port.type)
#         print("port index: %x" % port.index)
#         mlx5_mlxdevm_port = container_of(port, "struct mlx5_mlxdevm_port", "dl_port")
#         print(mlx5_mlxdevm_port.vport.vport)
#         netdev = Object(prog, 'struct net_device', address=port.type_dev)
#         print(netdev.name)
#         print("\n\tport index: %x" % port.index)
#         if port.index & 0xffff == 0xffff:
#              print(port.attrs)

    continue
    for node in radix_tree_for_each(mlxdevm.params.address_of_()):
#         print(node)
        param = Object(prog, 'struct mlxdevm_param_item', address=node[1].value_())
#         if param.driverinit_value_valid:
        print(param)
        print(param.param.name)
#     print("=== mlxdevm.param_list ===")
#     print(mlxdevm.param_list)
#     for item in list_for_each_entry('struct mlxdevm_param_item', mlxdevm.param_list.address_of_(), 'list'):
        print("-------------------------------------------------------------")
#         print(item)
#         print(item.param.id)
