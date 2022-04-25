#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5e_priv(pf0_name)
mlx5_sf_table = mlx5e_priv.mdev.priv.sf_table
# print(mlx5_sf_table)

mlx5_sf_hwc_table = mlx5e_priv.mdev.priv.sf_hw_table
print(mlx5_sf_hwc_table.hwc[0])

#         .port_index = (unsigned int)32769,
#         .controller = (u32)0,
#         .id = (u16)1,
#         .hw_fn_id = (u16)32769,
#         .hw_state = (u16)3,

print(" === sf rep === ")

def print_mlx5_sf(sf):
    print("port_index: %d, controller: %d, id: %d, hw_fn_id: %d, hw_state: %d" % \
        (sf.port_index, sf.controller, sf.id, sf.hw_fn_id, sf.hw_state))

for node in radix_tree_for_each(mlx5_sf_table.port_indices.address_of_()):
    mlx5_sf = Object(prog, 'struct mlx5_sf', address=node[1].value_())
    print_mlx5_sf(mlx5_sf)
#     print(mlx5_sf)

mlx5_nb = mlx5e_priv.mdev.priv.eswitch.nb
# print(mlx5_nb)

# n_head = mlx5e_priv.mdev.priv.eswitch.n_head
# n_head = mlx5e_priv.mdev.priv.vhca_state_notifier.n_head
# print(n_head)

# notifier_block = n_head.head
# while True:
#     if notifier_block.value_() == 0:
#         break
#     print(notifier_block)
#     mlx5_sf_table = container_of(notifier_block, "struct mlx5_sf_table", "esw_nb");
#     print(mlx5_sf_table)
#     notifier_block = notifier_block.next

print(" === sf === ")

mlx5_sf_dev_table = mlx5e_priv.mdev.priv.sf_dev_table
for node in radix_tree_for_each(mlx5_sf_dev_table.devices.address_of_()):
    mlx5_sf_dev = Object(prog, 'struct mlx5_sf_dev', address=node[1].value_())
    print(mlx5_sf_dev.adev.dev.kobj.name.string_().decode())
#     print(mlx5_sf_dev)

# (struct mlx5_sf_dev){
#         .adev = (struct auxiliary_device){
#                 .dev = (struct device){
#                         .kobj = (struct kobject){
#                                 .name = (const char *)0xffff9660120d3de0 = "mlx5_core.sf.2",

exit(0)

print('')
dev_head = prog['dev_head']
print("dev_head list")
# print(dev_head)
for mlx5_devm_device in list_for_each_entry('struct mlx5_devm_device', dev_head.address_of_(), 'list'):
    print('=============================================')
    print(mlx5_devm_device.device.device.kobj.name)
    print(mlx5_devm_device.device.ops)
#     print(mlx5_devm_device.device)

    for mlxdevm_rate_group in list_for_each_entry('struct mlxdevm_rate_group', mlx5_devm_device.device.rate_group_list.address_of_(), 'list'):
        print(mlxdevm_rate_group)

    for mlx5_devm_port in list_for_each_entry('struct mlx5_devm_port', mlx5_devm_device.device.port_list.address_of_(), 'port.list'):
        print(mlx5_devm_port)
