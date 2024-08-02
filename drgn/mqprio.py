#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    addr = dev.value_()
    ops = address_to_name(hex(dev.netdev_ops))
    if name not in "enp8s0f0":
        continue;
    print("===================================================")
    print(name)
    print(ops)

    print("dev.num_tc: %d" % dev.num_tc)
    print(dev.tc_to_txq)
    print("dev.real_num_tx_queues: %d" % dev.real_num_tx_queues)
#     print(dev.dcbnl_ops)

    mlx5e_priv = get_mlx5(dev)
    print("mlx5e_priv.channels.params.mqprio")
    print(mlx5e_priv.channels.params.mqprio)
    print(mlx5e_priv.mqprio_rl)
    n = mlx5e_priv.mqprio_rl.num_tc
    print("mlx5e_priv.mqprio_rl.leaves_id")
    for i in range(n):
        print(mlx5e_priv.mqprio_rl.leaves_id[i])

    print('\t', end='')
    print('')
