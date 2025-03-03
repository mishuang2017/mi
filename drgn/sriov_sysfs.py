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

def print_ktype(ktype):
    print(ktype)
#     default_groups = ktype.default_groups
#     print(default_groups)
#     print(default_groups[0])
    attrs = default_groups[0].attrs
    print(attrs)
    j = 0
    while True:
        if attrs[j]:
            print("--------------------------------------")
#             vf_attr = cast("struct vf_attributes *", attrs[j])
            vf_attr = container_of(attrs[j], "struct vf_attributes", "attr")
            print(vf_attr)
        else:
            break;
        j = j + 1


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
    sriov = esw.dev.priv.sriov
    print(sriov)
    print("esw->dev->priv->sriov.num_vfs: %d" % sriov.num_vfs)
#     for i in range(sriov.num_vfs):
    for i in range(1):
        print("========================== vf %d =========================" % i)
#         print(sriov.vfs[i])
        ktype = sriov.vfs[i].kobj.ktype
        print(ktype)
#         print_ktype(ktype)
#     print(sriov)
    groups_config = sriov.groups_config
    print(groups_config.ktype)
#     mlx5_esw_rate_group = container_of(groups_config, "struct mlx5_esw_rate_group", "kobj")
#     print(mlx5_esw_rate_group)

#     config = sriov.config
#     print(config.ktype)

#     print(groups_config.sd)
#     print(sriov.groups_create_attr)

print("===================== port 1 =======================")
print(pf0_name)
mlx5e_priv = get_mlx5e_priv(pf0_name)
print_esw(mlx5e_priv)
# print(mlx5e_priv.netdev.devlink_port.switch_port)

# vf_eth_attrs = prog['vf_eth_attrs']
# print(vf_eth_attrs)
# vf_type_eth = prog['vf_type_eth']
# print_ktype(vf_type_eth)

exit(0)

print("===================== port 2 =======================")
mlx5e_priv2 = get_mlx5e_priv(pf1_name)
print_esw(mlx5e_priv2)
