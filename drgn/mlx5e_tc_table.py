#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

mlx5e_priv = get_mlx5_pf0()
# print(mlx5e_priv)
mlx5e_tc_table = mlx5e_priv.fs.tc
# print(mlx5e_tc_table.chains)
print(mlx5e_tc_table.chains.dev.priv.eswitch)
# print(mlx5e_tc_table.netdevice_nb)
# print(mlx5e_tc_table.netdevice_nn)

# mlx5e_l2_table = mlx5e_priv.fs.l2
# print(mlx5e_l2_table)
# a = mlx5e_l2_table.promisc.addr
# print_mlx5_flow_handle(mlx5e_l2_table.promisc.rule)
# print("%x:%x:%x:%x:%x:%x:%x:%x" % (a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]))
