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

# prog = drgn.program_from_core_dump("/var/crash/vmcore.4")
# prog = drgn.program_from_kernel()
devlinks = prog['devlinks']
# print(devlinks)
for node in radix_tree_for_each(devlinks.address_of_()):
    devlink = Object(prog, 'struct devlink', address=node[1].value_())
    pci_name = devlink.dev.kobj.name.string_().decode()
#     if pci_name != "0000:08:00.0":
#         continue
#     print(devlink.ops)

# devlink ffff91b683000000
# devlink.dev.kobj.name: mlx5_core.sf.2
#         auxiliary_device.name: sf
#         auxiliary_device.id: 2
# mlx5_sf_dev_probe
# mlx5_sf_dev_remove
# mlx5_sf_dev_shutdown
# mlx5_core_dev ffff91b683000140
#         port index: a0000
# 
# devlink ffff91b647200000
# devlink.dev.kobj.name: mlx5_core.sf.3
#         auxiliary_device.name: sf
#         auxiliary_device.id: 3
# mlx5_sf_dev_probe
# mlx5_sf_dev_remove
# mlx5_sf_dev_shutdown
# mlx5_core_dev ffff91b647200140
#         port index: b0000
# 

# [root@c-141-27-1-009 ~]# trace mlx5_sf_dev_remove -K
# TIME     PID     TID     COMM            FUNC
# 7.963407 200234  200234  kworker/u16:3   mlx5_sf_dev_remove
#         mlx5_sf_dev_remove+0x1 [mlx5_core]
#         auxiliary_bus_remove +0x1c [auxiliary]
#         device_release_driver_internal +0xf1 [kernel]
#         bus_remove_device+0xf4 [kernel]
#         device_del+0x16f [kernel]
#         mlx5_sf_dev_state_change_handler +0x268 [mlx5_core]
#         notifier_call_chain+0x45 [kernel]
#         blocking_notifier_call_chain+0x3e [kernel]
#         mlx5_vhca_state_work_handler+0xc5 [mlx5_core]
#         process_one_work+0x1a2 [kernel]
#         worker_thread+0x30 [kernel]
#         kthread+0x110 [kernel]
#         ret_from_fork+0x1f [kernel]

#
# mlxdevm port add pci/0000:08:00.0 flavour pcisf pfnum 0 sfnum 88
#
# TIME     PID     TID     COMM            FUNC
# 10.95109 484113  484113  mlxdevm         register_netdev
#         register_netdev+0x1 [kernel]
#         mlx5e_vport_rep_load +0x274 [mlx5_core]
#         mlx5_esw_offloads_rep_load +0x66 [mlx5_core]
#         mlx5_esw_offloads_sf_vport_enable +0x93 [mlx5_core]
#         mlx5_devlink_sf_port_new +0x296 [mlx5_core]
#         mlx5_devm_sf_port_new +0x76 [mlx5_core]
#         mlxdevm_nl_cmd_port_new_doit+0x104 [mlxdevm]
#         genl_family_rcv_msg+0x1cf [kernel]
#         genl_rcv_msg+0x47 [kernel]
#         netlink_rcv_skb+0x49 [kernel]
#         genl_rcv+0x24 [kernel]
#         netlink_unicast+0x198 [kernel]
#         netlink_sendmsg+0x204 [kernel]
#         sock_sendmsg+0x30 [kernel]
#         __sys_sendto+0xee [kernel]
#         __x64_sys_sendto+0x24 [kernel]
#         do_syscall_64+0x55 [kernel]
#         entry_SYSCALL_64_after_hwframe+0x65 [kernel]

# [root@c-141-27-1-009 ~]# mlxdevm port del eth2
# [root@c-141-27-1-009 ~]# trace unregister_netdev -K
# TIME     PID     TID     COMM            FUNC
# 6.294196 484430  484430  mlxdevm         unregister_netdev
#         unregister_netdev+0x1 [kernel]
#         mlx5e_vport_rep_unload+0x6d [mlx5_core]
#         mlx5_esw_offloads_sf_vport_disable +0x14 [mlx5_core]
#         mlx5_devlink_sf_port_del +0x68 [mlx5_core]
#         mlxdevm_nl_cmd_port_del_doit+0x54 [mlxdevm]
#         genl_family_rcv_msg+0x1cf [kernel]
#         genl_rcv_msg+0x47 [kernel]
#         netlink_rcv_skb+0x49 [kernel]
#         genl_rcv+0x24 [kernel]
#         netlink_unicast+0x198 [kernel]
#         netlink_sendmsg+0x204 [kernel]
#         sock_sendmsg+0x30 [kernel]
#         __sys_sendto+0xee [kernel]
#         __x64_sys_sendto+0x24 [kernel]
#         do_syscall_64+0x55 [kernel]
#         entry_SYSCALL_64_after_hwframe+0x65 [kernel]

 
    print("devlink.dev.kobj.name: %s" % pci_name)
#     print(devlink)
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
#     mlx5_core_dev = Object(prog, 'struct mlx5_core_dev', address=devlink.priv.address_of_().value_())
#     print("mlx5_core_dev %x" % mlx5_core_dev.address_of_())
    print("=== devlink_port ===")
    for port in list_for_each_entry('struct devlink_port', devlink.port_list.address_of_(), 'list'):
        print("\n\tport index: %x" % port.index)
#         if port.index & 0xffff == 0xffff:
#              print(port.attrs)
