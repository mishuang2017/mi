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
    print("mlx5e_priv.fs.state_destroy %#x" % priv.fs.state_destroy.value_())
    print(priv.mdev.coredev_type)
    esw = priv.mdev.priv.eswitch
    print("mlx5_eswitch %#x" % esw)
    print("mode: %d" % esw.mode)
    if esw.mode == 0:
        return
    print("esw->fdb_table->flags: %x" % esw.fdb_table.flags);
    print("esw->total_vports: %d" % esw.total_vports)
    print("esw->enabled_vports: %d" % esw.enabled_vports)
    print("esw->manager_vport: %d" % esw.manager_vport)
    print("esw->esw_funcs->num_vfs: %d" % esw.esw_funcs.num_vfs)
    print("esw->dev->priv->sriov.num_vfs: %d" % esw.dev.priv.sriov.num_vfs)
    for i in range(esw.dev.priv.sriov.num_vfs):
        print(esw.dev.priv.sriov.vfs[i])
        ktype = esw.dev.priv.sriov.vfs[i].kobj.ktype
        print(ktype)
        default_groups = ktype.default_groups
        print(default_groups[0])
        attrs = default_groups[0].attrs
        print(attrs)
        j = 0
        while True:
            if attrs[j]:
                print(attrs[j])
            else:
                break;
            j = j + 1
#     print(esw.dev.priv.sriov.config)

print("===================== port 1 =======================")
print(pf0_name)
mlx5e_priv = get_mlx5e_priv(pf0_name)
print_esw(mlx5e_priv)
# print(mlx5e_priv.netdev.devlink_port.switch_port)

exit(0)

print("===================== port 2 =======================")
mlx5e_priv2 = get_mlx5e_priv(pf1_name)
print_esw(mlx5e_priv2)
