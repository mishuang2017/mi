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

devlinks = prog['devlinks']
# print(devlinks)
for node in radix_tree_for_each(devlinks.address_of_()):
    devlink = Object(prog, 'struct devlink', address=node[1].value_())
    pci_name = devlink.dev.kobj.name.string_().decode()
    print("devlink.dev.kobj.name: %s" % pci_name)
    mlx5_core_dev = Object(prog, 'struct mlx5_core_dev', address=devlink.priv.address_of_())
    print("mlx5_core_dev %x" % mlx5_core_dev.address_of_())
    print(mlx5_core_dev.coredev_type)
    for i in range(6):
        if mlx5_core_dev.priv.adev[i]:
#             print(mlx5_core_dev.priv.adev[i].adev)
            print(mlx5_core_dev.priv.adev[i].adev.dev.kobj.name)
    print('')


#         .adev = (struct auxiliary_device){
#                 .dev = (struct device){
#                         .kobj = (struct kobject){
#                                 .name = (const char *)0xffff9c565c9904a0 = "mlx5_core.rdma.6",
