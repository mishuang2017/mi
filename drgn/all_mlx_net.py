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
#     print(dev.netdev_ops)
    ops = address_to_name(hex(dev.netdev_ops))
    if "mlx5e" not in ops:
        continue;
#     if name not in "en8f0pf0sf1":
#         continue;
#     if name not in "enp8s0f0":
#         continue;
    print("===================================================")
    print(name)
    print(dev.netdev_ops.ndo_get_port_parent_id)

    print("dev.num_tc: %d" % dev.num_tc)
    print(dev.tc_to_txq)
    print("dev.real_num_tx_queues: %d" % dev.real_num_tx_queues)
#     print(dev.ethtool_ops)
#     print(dev.dcbnl_ops)

#     if dev.devlink_port:
#         dl_port = dev.devlink_port
#         for i in range(dl_port.attrs.switch_id.id_len):
#             print("%02x:" % dl_port.attrs.switch_id.id[i], end='')
#         print('')

    mlx5e_priv_addr = addr + prog.type('struct net_device').size
    mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)
    print(mlx5e_priv.mdev.caps.embedded_cpu)
#     print(mlx5e_priv.aso)
#     print("wq: %x" % mlx5e_priv.wq)
#     print(mlx5e_priv.ipsec)
#     print(mlx5e_priv.vhca_id)
#     print(mlx5e_priv.fs.tc.netdevice_nb.notifier_call)
#     print("mlx5e_priv_addr: %x" % mlx5e_priv_addr)
#     print(mlx5e_priv)
#     print(mlx5e_priv.init)
#     print(mlx5e_priv.fs.vlan_strip_disable)
#     if name in "enp8s0f0":
#             print(dev.page_pools)
#             for pool in hlist_for_each_entry('struct page_pool', dev.page_pools.address_of_(), 'user.list'):
#                 print(pool.alloc)
#         print("yes")
#         print(mlx5e_priv.channels.params.mqprio)

#     ppriv = mlx5e_priv.ppriv
#     if ppriv:
#         print("ppriv %lx" % ppriv.value_())
#         mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())
#     print(mlx5e_priv.profile)

    print('\t', end='')
    print('')
