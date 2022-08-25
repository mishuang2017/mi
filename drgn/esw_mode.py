#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *


def print_esw(priv):
    esw = mlx5e_priv.mdev.priv.eswitch
    print("mlx5_core_dev %#x" % priv.mdev)
    print("esw->flags: %#x" % esw.flags)
    print("mode: %d" % esw.mode)
    print("fdb_table.flags: %x" % esw.fdb_table.flags);
    print("total_vports: %d" % esw.total_vports)
    print("enabled_vports: %d" % esw.enabled_vports)
    print("esw->manager_vport: %d" % esw.manager_vport)
    print("esw->esw_funcs.num_vfs: %d" % esw.esw_funcs.num_vfs)
    print("esw->dev->priv.sriov.num_vfs: %d" % esw.dev.priv.sriov.num_vfs)
    print("esw.fdb_table.offloads.send_to_vport_meta_grp: %x" % esw.fdb_table.offloads.send_to_vport_meta_grp)
    print("esw->fdb_table.offloads.send_to_vport_meta_rules: %d" % esw.fdb_table.offloads.send_to_vport_meta_rules)
    print("esw->offloads.inline_mode: %d" % esw.offloads.inline_mode)
    print(esw.user_count)
    print(esw.offloads.num_flows)

mlx5e_priv = get_mlx5e_priv(pf0_name)
print_esw(mlx5e_priv)
mlx5e_priv2 = get_mlx5e_priv(pf1_name)
print_esw(mlx5e_priv2)
