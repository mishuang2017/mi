#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append('.')
from lib import *

# struct mlx5_eswitch_rep

def print_meter(mlx5e_priv):
    mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
    print(mlx5e_priv.ppriv)
    vports = mlx5_eswitch.offloads.vport_reps
    total_vports = mlx5_eswitch.total_vports
    enabled_vports = mlx5_eswitch.enabled_vports

    print("esw mode: %d" % mlx5_eswitch.mode)
    print("total_vports: %d" % total_vports)
    print("enabled_vports: %d" % enabled_vports)

    # vport_reps = mlx5e_priv.mdev.priv.eswitch.offloads.vport_reps
    # for i in range(3):
    #     print(vport_reps[i])
    # print(vport_reps[total_vports - 1])

    i=1
    for node in radix_tree_for_each(vports):
        i=i+1
        mlx5_eswitch_rep = Object(prog, 'struct mlx5_eswitch_rep', address=node[1].value_())
        if mlx5_eswitch_rep.vport != 0xffff:
            continue
        mlx5e_rep_priv = mlx5_eswitch_rep.rep_data[0].priv
        print("=== %d ===" % mlx5_eswitch_rep.vport)
        print("mlx5e_rep_priv: %x" % mlx5e_rep_priv)
        print(mlx5e_rep_priv)
        if mlx5e_rep_priv:
            mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=mlx5e_rep_priv)
#                 print(mlx5e_rep_priv.netdev.name)
    #             print(" ================== drop_red_rule ==================")
    #             print_mlx5_flow_handle(rep_meter.drop_red_rule)
    #             print(" ================== end drop_red_rule ==================")
    #             print(rep_meter.meter_hndl)
    #             print(rep_meter.meter_hndl.flow_meters)
    #             print(" ============  handle ===============")
    #             flow_meters = rep_meter.meter_hndl.flow_meters
    #             print(" ============ end handle ===============")
    #             print(rep_meter.meter_hndl.flow_meters.aso)
#                 print("rep_meter.meter_hndl.obj_id: %d, rep_meter.meter_hndl.idx: %d" %
#                     (rep_meter.meter_hndl.obj_id, rep_meter.meter_hndl.idx))
    #             print(rep_meter.meter_hndl.meters_obj.meters_map[0])
    #             print("\nrep_meter.meter_rule")
    #             print_mlx5_flow_handle(rep_meter.meter_rule)
#                 print(rep_meter)
#                 print(rep_meter.drop_counter.id)

    # print(mlx5e_priv.aso)
            uplink_priv = mlx5e_rep_priv.uplink_priv
            flow_meters = uplink_priv.flow_meters
#             print(flow_meters)
            for i in range(256):
                for handle in hlist_for_each_entry('struct mlx5e_flow_meter_handle', flow_meters.hashtbl[i], 'hlist'):
                    print(handle)
#     print(" ======================== uplink_priv.flow_meters ==================")
#     print(uplink_priv.flow_meters)
#     post_meter = uplink_priv.flow_meters.post_meter
#     print(post_meter)
    # flow_table("post_meter", post_meter.ft)
    # print(" ================== fwd_green_rule ==================")
    # print_mlx5_flow_handle(post_meter.fwd_green_rule)
    # print(" ================== drop_red_rule ==================")
    # print_mlx5_flow_handle(post_meter.drop_red_rule)
    # print(" ======================== end uplink_priv.flow_meters ==================")

mlx5e_priv = get_mlx5_pf0()
print_meter(mlx5e_priv)

# print('---------------------------------------')

# mlx5e_priv = get_mlx5_pf1()
# print_meter(mlx5e_priv)

print("\n-------------------------------\n")
gen = prog['init_net'].gen
id = prog['police_net_id']
print("police_id: %d" % id)
ptr = gen.ptr[id]
tc_action_net = Object(prog, 'struct tc_action_net', address=ptr.value_())
# print(tc_action_net)
idr=tc_action_net.idrinfo.action_idr

for node in radix_tree_for_each(idr.idr_rt.address_of_()):
    print(node)
    fc = Object(prog, 'struct mlx5_fc', address=node[1].value_())
    print("id: %x, packets: %d" % (fc.id, fc.cache.packets))
