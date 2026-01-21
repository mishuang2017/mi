#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5e_priv(pf0_name)
dev = mlx5e_priv.netdev
# print(dev.xfrmdev_ops)
# exit(0)

xfrm_state_dev_gc_list = prog['xfrm_state_dev_gc_list']
print(xfrm_state_dev_gc_list)

exit(0)

ipsec = mlx5e_priv.ipsec
print(ipsec)
print(mlx5e_priv.netdev.xfrmdev_ops)

sadb = ipsec.sadb
print("\n======================== sadb ===========================\n")
# print(sadb)

# crypto
# flow_table("sa", ipsec.tx.ft.sa)
# flow_table("sa", ipsec.tx.ft.pol)

for node in radix_tree_for_each(sadb.address_of_()):
    print(node)
    entry = Object(prog, 'struct mlx5e_ipsec_sa_entry', address=node[1].value_())
    print(entry)


MLX5_ESWITCH_OFFLOADS = prog['MLX5_ESWITCH_OFFLOADS']
MLX5_ESWITCH_LEGACY = prog['MLX5_ESWITCH_LEGACY']

if mlx5e_priv.mdev.priv.eswitch.mode == MLX5_ESWITCH_LEGACY:
    print("\n======================== legacy ===========================\n")
    tx = ipsec.tx
    rx = ipsec.rx_ipv4
    # print(tx)
    print("\n--- policy ---\n")
    flow_table("ipsec.tx.pol", tx.ft.pol)
    flow_table("ipsec.rx.pol", rx.ft.pol)

    print("\n--- stat ---\n")
    flow_table("ipsec.tx.sa", tx.ft.sa)
    flow_table("ipsec.rx.sa", rx.ft.sa)

else:
    print("\n======================== switchdev ===========================\n")
    tx = ipsec.tx_esw
    rx = ipsec.rx_esw
    print(tx.ft)
    print("\n--- policy ---\n")
    flow_table("ipsec.tx.pol", tx.ft.pol)
    flow_table("ipsec.rx.pol", rx.ft.pol)

    print("\n--- stat ---\n")
    flow_table("ipsec.tx.sa", tx.ft.sa)
    flow_table("ipsec.rx.sa", rx.ft.sa)

    print("\n--- status ---\n")
    flow_table("ipsec.tx.status", tx.ft.status)
    flow_table("ipsec.rx.status", rx.ft.status)

    print("\n--- fc ---\n")
    print(tx.fc.cnt)
    print(rx.fc.cnt)

    print(ipsec.tx.fc.cnt)
    print(ipsec.rx_ipv4.fc.cnt)

    print("\n--- ft_ipsec_tx_pol ---\n")
    flow_table("ft_ipsec_tx_pol", mlx5e_priv.mdev.priv.eswitch.offloads.ft_ipsec_tx_pol);
# exit(0)

def print_counters():
    print("\n======================== counters ===========================\n")

    fc = ipsec_priv.decap_rule_counter
    print("decap_rule_counter       id: %x, packets: %d" % (fc.id, fc.cache.packets))
    fc = ipsec_priv.decap_miss_rule_counter
    print("decap_miss_rule_counter  id: %x, packets: %d" % (fc.id, fc.cache.packets))

    fc = ipsec_priv.tx_chk_rule_counter
    print("tx_chk_rule_counter      id: %x, packets: %d" % (fc.id, fc.cache.packets))
    fc = ipsec_priv.tx_chk_drop_rule_counter
    print("tx_chk_drop_rule_counter id: %x, packets: %d" % (fc.id, fc.cache.packets))

# print_counters()
