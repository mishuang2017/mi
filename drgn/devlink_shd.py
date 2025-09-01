#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

shd_list = prog['shd_list']
# print(shd_list)

for mlx5_shd in list_for_each_entry('struct mlx5_shd', shd_list.address_of_(), 'list'):
    print(mlx5_shd)
    print("mlx5_shd.faux_dev.dev.driver_data", end=' ')
    print(mlx5_shd.faux_dev.dev.driver_data)
    devlink = container_of(mlx5_shd, "struct devlink", "priv")
#     print(devlink.dev.kobj)

devlink_rels = prog['devlink_rels']
for node in radix_tree_for_each(devlink_rels.address_of_()):
    print('-------------------------------------')
    rel = Object(prog, 'struct devlink_rel', address=node[1].value_())
    print("rel.index: %d, rel.devlink_index: %d, nested_in.devlink_index: %d" % (rel.index, rel.devlink_index, rel.nested_in.devlink_index))
#     print(rel)
