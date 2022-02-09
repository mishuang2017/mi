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
print("esw->flags: %#x" % esw.flags)
print("mode: %d" % esw.mode)
print("fdb_table.flags: %x" % esw.fdb_table.flags);
print("enabled_vports: %d" % esw.enabled_vports)
print("esw_funcs.num_vfs: %d" % esw.esw_funcs.num_vfs)
print("esw->dev->priv.sriov.num_vfs: %d" % esw.dev.priv.sriov.num_vfs)
print("esw.fdb_table.offloads.send_to_vport_meta_grp: %x" % esw.fdb_table.offloads.send_to_vport_meta_grp)
print("esw->fdb_table.offloads.send_to_vport_meta_rules: %d" % esw.fdb_table.offloads.send_to_vport_meta_rules)

if type_exist("enum mlx5_eswitch_action"):
    if esw.mode.value_() == 1:
        flow_table("esw.fdb_table.offloads.slow_fdb", esw.fdb_table.offloads.slow_fdb)
else:
    if esw.mode.value_() == 1:
        if esw.fdb_table.legacy.fdb:
            flow_table("legacy", esw.fdb_table.legacy.fdb)
        else:
            print("legacy fdb is 0")

    if esw.mode.value_() == 2:
        flow_table("esw.fdb_table.offloads.slow_fdb", esw.fdb_table.offloads.slow_fdb)
