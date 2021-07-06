#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import reinterpret
import time
import socket

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

print(pf1_name)

mlx5e_priv = get_mlx5e_priv(pf0_name)
mlx5_eswitch_fdb = mlx5e_priv.mdev.priv.eswitch.fdb_table

slow_fdb = mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.slow_fdb
flow_table("mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.slow_fdb", slow_fdb)

# sys.exit(0)
vport_to_tir = mlx5e_priv.mdev.priv.eswitch.offloads.ft_offloads
flow_table("mlx5e_priv.mdev.priv.eswitch.offloads.ft_offloads", vport_to_tir)

print("\nmlx5e_priv->ppriv(mlx5e_rep_priv)->root_ft")
for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    if pf0_name in name:
        print(name)
        mlx5e_priv_addr = dev.value_() + prog.type('struct net_device').size
        mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)
        ppriv = mlx5e_priv.ppriv
        if ppriv:
            mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())
            print("mlx5_flow_table %lx" % mlx5e_rep_priv.root_ft.value_())
            print_dest(mlx5e_rep_priv.vport_rx_rule.rule[0])
#             flow_table(name, mlx5e_rep_priv.vport_rx_rule.rule[0].dest_attr.ft)
