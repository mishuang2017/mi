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

def print_slow_fdb(name):
    print("==============================%s===============================" % name)
    mlx5e_priv = get_mlx5e_priv(name)
    mlx5_eswitch_fdb = mlx5e_priv.mdev.priv.eswitch.fdb_table

    slow_fdb = mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.slow_fdb
    tc_miss_table = mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.tc_miss_table
    # flow_table("mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.tc_miss_table", tc_miss_table)
    flow_table("mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.slow_fdb", slow_fdb)

    # miss_meter_fdb = mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.miss_meter_fdb
    # flow_table("mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.miss_meter_fdb", miss_meter_fdb)

    # post_miss_meter_fdb = mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.post_miss_meter_fdb
    # flow_table("mlx5e_priv.mdev.priv.eswitch.fdb_table.offloads.post_miss_meter_fdb", post_miss_meter_fdb)

    vport_to_tir = mlx5e_priv.mdev.priv.eswitch.offloads.ft_offloads
    print("\n====================== vport_to_tir ========================")
    flow_table("mlx5e_priv.mdev.priv.eswitch.offloads.ft_offloads", vport_to_tir)

print_slow_fdb(pf0_name)
print_slow_fdb(pf1_name)

# exit(0)

print("\nmlx5e_priv->ppriv(mlx5e_rep_priv)->root_ft")
for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    if pf0_name in name or pf1_name in name:
        mlx5e_priv_addr = dev.value_() + prog.type('struct net_device').size
        mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)
        ppriv = mlx5e_priv.ppriv
        if ppriv:
            print('----------------------------------')
            print(name)
            mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())
            print(" mlx5e_rep_priv.root_ft: mlx5_flow_table %lx" % mlx5e_rep_priv.root_ft.value_())
#             print_dest(mlx5e_rep_priv.vport_rx_rule.rule[0])
#             flow_table(name, mlx5e_rep_priv.vport_rx_rule.rule[0].dest_attr.ft)

            vport_sqs_list = mlx5e_rep_priv.vport_sqs_list
            i = 0;
            for mlx5e_rep_sq in list_for_each_entry('struct mlx5e_rep_sq', vport_sqs_list.address_of_(), 'list'):
                print('mlx5e_rep_sq.send_to_vport_rule, index: %d, sqn: %d, %#x' % (i, mlx5e_rep_sq.sqn, mlx5e_rep_sq.sqn))
                print_mlx5_flow_handle(mlx5e_rep_sq.send_to_vport_rule)
                i = i + 1
