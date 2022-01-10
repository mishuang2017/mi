#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5e_priv(pf0_name)
esw = mlx5e_priv.mdev.priv.eswitch
print("mode: %d" % esw.mode)
print("enabled_vports: %d" % esw.enabled_vports)
print("esw_funcs.num_vfs: %d" % esw.esw_funcs.num_vfs)
print("esw->dev->priv.sriov.num_vfs: %d" % esw.dev.priv.sriov.num_vfs)

if hostname.find("c-235-253-1-007") == 0:
    if esw.mode.value_() == 0:
        if esw.fdb_table.legacy.fdb and esw.fdb_table.legacy.fdb.id:
            flow_table("legacy", esw.fdb_table.legacy.fdb)
        else:
            print("legacy fdb is 0")

    if esw.mode.value_() == 1:
        flow_table("offloads", esw.fdb_table.offloads.slow_fdb)
else:
    if esw.mode.value_() == 1:
        if esw.fdb_table.legacy.fdb:
            flow_table("legacy", esw.fdb_table.legacy.fdb)
        else:
            print("legacy fdb is 0")

    if esw.mode.value_() == 2:
        flow_table("offloads", esw.fdb_table.offloads.slow_fdb)
