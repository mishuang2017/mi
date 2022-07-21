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
print("total_vports: %d" % esw.total_vports)
print("enabled_vports: %d" % esw.enabled_vports)
print("esw_funcs.num_vfs: %d" % esw.esw_funcs.num_vfs)
print("esw->manager_vport: %d" % esw.manager_vport)
print("esw->dev->priv.sriov.num_vfs: %d" % esw.dev.priv.sriov.num_vfs)
print("esw.fdb_table.offloads.send_to_vport_meta_grp: %x" % esw.fdb_table.offloads.send_to_vport_meta_grp)
print("esw->fdb_table.offloads.send_to_vport_meta_rules: %d" % esw.fdb_table.offloads.send_to_vport_meta_rules)
print("esw->offloads.inline_mode: %d" % esw.offloads.inline_mode)

new = 1
if new:
    if esw.mode.value_() == 0:
        if not esw.fdb_table.legacy.fdb:
            print("legacy fdb is 0")
    elif esw.mode.value_() == 1:
        flow_table("esw.fdb_table.offloads.slow_fdb", esw.fdb_table.offloads.slow_fdb)
else:
    if esw.mode.value_() == 1:
        if not esw.fdb_table.legacy.fdb:
            print("legacy fdb is 0")
    elif esw.mode.value_() == 2:
        flow_table("esw.fdb_table.offloads.slow_fdb", esw.fdb_table.offloads.slow_fdb)
