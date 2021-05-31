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
# import lib

# prog = drgn.program_from_core_dump("/var/crash/vmcore.4")
prog = drgn.program_from_kernel()
devlink_list = prog['devlink_list']
print("devlink_list %x" % devlink_list.address_of_())
for devlink in list_for_each_entry('struct devlink', devlink_list.address_of_(), 'list'):
    print('')
    print("devlink %x" % devlink)
    pci_name = devlink.dev.kobj.name.string_().decode()
#     print(devlink)
#     if pci_name != "0000:04:00.0":
#         continue
    print(pci_name)
#     print(devlink._net)
#     print(devlink.ops.reload_down)
#     print(devlink.ops.reload_up)
    mlx5_core_dev = Object(prog, 'struct mlx5_core_dev', address=devlink.priv.address_of_().value_())
    print("mlx5_core_dev %x" % mlx5_core_dev.address_of_())
    for port in list_for_each_entry('struct devlink_port', devlink.port_list.address_of_(), 'list'):
        print("\tport index: %x" % port.index)
        if port.index & 0xffff == 0xffff:
             print(port.attrs)
