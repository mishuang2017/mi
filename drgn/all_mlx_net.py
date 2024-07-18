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
#     if "mlx5e" not in ops:
#         continue;
#     if name not in "en8f0pf0sf1":
#         continue;
    print(name)
    print(ops)

    if dev.devlink_port:
        dl_port = dev.devlink_port
        for i in range(dl_port.attrs.switch_id.id_len):
            print("%02x:" % dl_port.attrs.switch_id.id[i], end='')
        print('')

    mlx5e_priv_addr = addr + prog.type('struct net_device').size
    mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)
#     print("wq: %x" % mlx5e_priv.wq)
#     print(mlx5e_priv.ipsec)
#     print(mlx5e_priv.vhca_id)
#     print(mlx5e_priv.fs.tc.netdevice_nb.notifier_call)
#     print("mlx5e_priv_addr: %x" % mlx5e_priv_addr)
#     print(mlx5e_priv)
#     print(mlx5e_priv.init)
#     print(mlx5e_priv.fs.vlan_strip_disable)
#     print(mlx5e_priv.channels.params)

#     ppriv = mlx5e_priv.ppriv
#     if ppriv:
#         print("ppriv %lx" % ppriv.value_())
#         mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())
#     print(mlx5e_priv.profile)

    print('\t', end='')
    print('')
