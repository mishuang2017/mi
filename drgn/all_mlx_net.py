#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

for x, dev in enumerate(lib.get_netdevs()):
    name = dev.name.string_().decode()
    addr = dev.value_()
    if "enp" not in name:
        continue;
    print(name)

    mlx5e_priv_addr = addr + prog.type('struct net_device').size
    mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)

    ppriv = mlx5e_priv.ppriv
    if ppriv:
        print("ppriv %lx" % ppriv.value_())
        mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())

    print('\t', end='')
    print('')
