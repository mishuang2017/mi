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

for pf in pf0_name, pf1_name:
    print("\n====================== %s ======================" % pf)
    mlx5e_priv = get_mlx5e_priv(pf)
    mlx5_eswitch_fdb = mlx5e_priv.mdev.priv.eswitch.fdb_table

    miss_meter_fdb = mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.miss_meter_fdb
    flow_table("mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.miss_meter_fdb", miss_meter_fdb)

    post_miss_meter_fdb = mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.post_miss_meter_fdb
    flow_table("mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.post_miss_meter_fdb", post_miss_meter_fdb)
