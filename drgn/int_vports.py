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

# struct mlx5_esw_offload
offloads = mlx5e_priv.mdev.priv.eswitch.offloads

int_vports = offloads.int_vports
print(int_vports)

for port in list_for_each_entry('struct mlx5_esw_int_vport', int_vports.address_of_(), 'list'):
    print(port)
