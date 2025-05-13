#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
import time
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

devices = prog['devices']

for node in radix_tree_for_each(devices):
    print('--------------------------')
    ib_device = Object(prog, 'struct ib_device', address=node[1].value_())
    print("index: %x" % ib_device.index)
    print("ib_device.phys_port_cnt: %d" % ib_device.phys_port_cnt)
#     print(ib_device.ops)
    print(ib_device.dma_device.release)
    mlx5_ib_dev = container_of(ib_device.address_of_(), "struct mlx5_ib_dev", "ib_dev")
    print(mlx5_ib_dev.mdev.device.kobj.name.string_().decode())
#     print(ib_device)

rdma_dev_net_id = prog['rdma_dev_net_id']
print("rdma_dev_net_id: %x " % rdma_dev_net_id)
