#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

mlxdevms = prog['mlxdevms']
# print(mlxdevms)

for node in radix_tree_for_each(mlxdevms.address_of_()):
#     print(node)
    mlxdevm = Object(prog, 'struct mlxdevm', address=node[1].value_())
#     print(mlxdevm.index)
    port_list = mlxdevm.port_list
#     print(port_list)
    for port in list_for_each_entry('struct mlxdevm_port', port_list.address_of_(), 'list'):
        print("%x" % port.index)
        print(port)
        devm = port.devm
        mlx5_devm_device = cast("struct mlx5_devm_device *", devm)
        mlx5_core_dev = mlx5_devm_device.dev
        devlink = container_of(mlx5_core_dev, "struct devlink" , "priv")
#         print(devlink)
