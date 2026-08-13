#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

print('')
dev_head = prog['dev_head']
print("dev_head list")
# print(dev_head)
for mlx5_devm_device in list_for_each_entry('struct mlx5_devm_device', dev_head.address_of_(), 'list'):
    print('=============================================')
    print(mlx5_devm_device.device.index)
    print(mlx5_devm_device.device.dev.kobj.name)
#     print(mlx5_devm_device.device.ops)

#     for mlxdevm_rate_group in list_for_each_entry('struct mlxdevm_rate_group', mlx5_devm_device.device.rate_group_list.address_of_(), 'list'):
#         print(mlxdevm_rate_group)

#     for mlx5_devm_port in list_for_each_entry('struct mlx5_devm_port', mlx5_devm_device.port_list.address_of_(), 'list'):
#         print("mlx5_devm_port.port_index: %d, %#x" % (mlx5_devm_port.port_index, mlx5_devm_port.port_index))
#         print("mlx5_devm_port.vport_num: %d, %#x" % (mlx5_devm_port.vport_num, mlx5_devm_port.vport_num))
#         for i in range(8):
#             print("%x%x%x%x" % mlx5_devm_port.port.dl_port.attrs.switch_id.id[i])
