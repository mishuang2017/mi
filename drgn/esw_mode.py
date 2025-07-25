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
#     print(priv.netdev.xfrmdev_ops)
#     print("mlx5e_priv %#x" % priv.address_of_())
    print("mlx5e_priv.fs.state_destroy %#x" % priv.fs.state_destroy.value_())
#     print(priv.mdev.mlx5e_res.ct)
    print("mlx5_core_dev.num_block_tc %d" % priv.mdev.num_block_tc)
    print("mlx5_core_dev.num_block_ipsec %d" % priv.mdev.num_block_ipsec)
    print(priv.mdev.coredev_type)

#     for i in range(priv.mdev.mlx5e_res.dl_port.attrs.switch_id.id_len):
#         print("%02x:" % priv.mdev.mlx5e_res.dl_port.attrs.switch_id.id[i], end='')

    print('')
    print("mlx5_priv %#x" % priv.mdev.priv.address_of_())
#     print_health(priv.mdev.priv.health)
    esw = priv.mdev.priv.eswitch
    print("mode: %d" % esw.mode)
    print("mlx5_eswitch %#x" % esw)
#     print(esw.qos)
#     return
    print("mlx5_core_dev %#x, %s" % (priv.mdev, priv.mdev.device.kobj.name.string_().decode()))
    print("esw->flags: %#x (1 means MLX5_ESWITCH_VPORT_MATCH_METADATA)" % esw.flags)
    print("steering->mode: %#x (1 mens MLX5_FLOW_STEERING_MODE_SMFS)" % priv.mdev.priv.steering.mode)
#     print(esw.offloads.ft_offloads)
    if esw.mode == 0:
        return
#     print(esw.qos.domain)
    print("esw->fdb_table->flags: %x" % esw.fdb_table.flags);
    print("esw->total_vports: %d" % esw.total_vports)
    print("esw->num_peers: %d" % esw.num_peers)
    print("esw->enabled_vports: %d" % esw.enabled_vports)
    print("esw->manager_vport: %d" % esw.manager_vport)
    print("esw->esw_funcs->num_vfs: %d" % esw.esw_funcs.num_vfs)
    print("esw->dev->priv->sriov.num_vfs: %d" % esw.dev.priv.sriov.num_vfs)
    print("esw->dev->priv->sriov.max_vfs: %d" % esw.dev.priv.sriov.max_vfs)
    print("esw->fdb_table->flags: %x" % esw.fdb_table.flags)
    print("esw->fdb_table->offloads->send_to_vport_meta_grp: %x" % esw.fdb_table.offloads.send_to_vport_meta_grp)
    print("esw->fdb_table->offloads->send_to_vport_meta_rules: %d" % esw.fdb_table.offloads.send_to_vport_meta_rules)
    print("esw->offloads->inline_mode: %d" % esw.offloads.inline_mode)
    print("esw->offloads->encap: %d" % esw.offloads.encap)
#     print(esw.offloads.rep_ops[0])
#     print(esw.offloads.rep_ops[1])
    print("user_count: %d" % esw.user_count.counter)
    print("num_flows %d" % esw.offloads.num_flows.counter)

#     print("-------------------------------")
#     for j in range(2):
#         if esw.fdb_table.offloads.peer_miss_rules[j]:
#             for i in range(esw.total_vports):
#                 print_mlx5_flow_handle(esw.fdb_table.offloads.peer_miss_rules[j][i])
#     print("-------------------------------")

#     print(esw.offloads.peer_flows)
#     for flow in list_for_each_entry('struct mlx5e_tc_flow', esw.offloads.peer_flows[1].address_of_(), 'peer'):
#         print("%x" % flow)
#         print_mlx5e_tc_flow(flow)

print("===================== port 1 =======================")
print(pf0_name)
mlx5e_priv = get_mlx5e_priv(pf0_name)
print_esw(mlx5e_priv)
# print(mlx5e_priv.netdev.devlink_port.switch_port)

# exit(0)

print("===================== port 2 =======================")
mlx5e_priv2 = get_mlx5e_priv(pf1_name)
print_esw(mlx5e_priv2)
