#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

def print_health(health):
    print(health.failed_in_seq)
#     print(health.fw_reporter)
    print(health.fw_fatal_reporter)

def print_esw(priv):
    print(priv.netdev.xfrmdev_ops)
    print("mlx5e_priv %#x" % priv.address_of_())
    print("mlx5_core_dev %#x" % priv.mdev)
    print("mlx5_priv %#x" % priv.mdev.priv.address_of_())
#     print_health(priv.mdev.priv.health)
    esw = mlx5e_priv.mdev.priv.eswitch
    print("mlx5_eswitch %#x" % esw)
    print("mlx5_core_dev %#x, %s" % (priv.mdev, priv.mdev.device.kobj.name.string_().decode()))
    print("esw->flags: %#x" % esw.flags)
    print("mode: %d" % esw.mode)
    print(esw.offloads.reg_c0_obj_pool)
    print(esw.offloads.ft_offloads)
    if esw.mode == 0:
        return
    print("esw->fdb_table->flags: %x" % esw.fdb_table.flags);
    print("esw->total_vports: %d" % esw.total_vports)
    print("esw->enabled_vports: %d" % esw.enabled_vports)
    print("esw->manager_vport: %d" % esw.manager_vport)
    print("esw->esw_funcs->num_vfs: %d" % esw.esw_funcs.num_vfs)
    print("esw->dev->priv->sriov.num_vfs: %d" % esw.dev.priv.sriov.num_vfs)
    print("esw->fdb_table->flags: %x" % esw.fdb_table.flags)
    print("esw->fdb_table->offloads->send_to_vport_meta_grp: %x" % esw.fdb_table.offloads.send_to_vport_meta_grp)
    print("esw->fdb_table->offloads->send_to_vport_meta_rules: %d" % esw.fdb_table.offloads.send_to_vport_meta_rules)
    print("esw->offloads->inline_mode: %d" % esw.offloads.inline_mode)
    print("user_count: %d" % esw.user_count.counter)
    print("num_flows %d" % esw.offloads.num_flows.counter)

    print(esw.offloads.peer_flows)
    for flow in list_for_each_entry('struct mlx5e_tc_flow', esw.offloads.peer_flows.address_of_(), 'peer'):
        print("%x" % flow)

print("===================== port 1 =======================")
mlx5e_priv = get_mlx5e_priv(pf0_name)
print_esw(mlx5e_priv)
# print("===================== port 2 =======================")
# mlx5e_priv2 = get_mlx5e_priv(pf1_name)
# print_esw(mlx5e_priv2)
