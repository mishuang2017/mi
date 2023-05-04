#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5e_priv(pf0_name)
ipsec = mlx5e_priv.ipsec
print(mlx5e_priv.netdev.xfrmdev_ops)

def print_sadb(sadb):
    for i in range(1024):
        node = sadb[i].first
        while node.value_():
            obj = container_of(node, "struct mlx5e_ipsec_sa_entry", "hlist")
            sa = Object(prog, 'struct mlx5e_ipsec_sa_entry', address=obj.value_())
            print(sa)
            print(sa.ipsec.aso)
            print(sa.ipsec.aso.maso)
            print(sa.ipsec.aso.umr)
            
            print_mlx5_flow_handle(sa.ipsec_rule.rule)

            node = node.next

sadb = ipsec.sadb_tx
print("\n======================== tx ===========================\n")
print_sadb(sadb)

sadb = ipsec.sadb_rx
print("\n======================== rx ===========================\n")
print_sadb(sadb)

# print(ipsec.aso)
# print(ipsec.aso.maso)

print("\n======================== ipsec_priv ===========================\n")
esw = mlx5e_priv.mdev.priv.eswitch
ipsec_priv = esw.fdb_table.offloads.esw_ipsec_priv
print(ipsec_priv)

print("\n======================== ipsec_fdb_crypto_rx ===========================\n")
flow_table("ipsec_fdb_crypto_rx", ipsec_priv.ipsec_fdb_crypto_rx)
print("\n======================== ipsec_fdb_decap_rx ===========================\n")
flow_table("ipsec_fdb_decap_rx", ipsec_priv.ipsec_fdb_decap_rx)

print("\n======================== ipsec_fdb_crypto_tx ===========================\n")
flow_table("ipsec_fdb_crypto_tx", ipsec_priv.ipsec_fdb_crypto_tx)
print("\n======================== ipsec_fdb_tx_chk ===========================\n")
flow_table("ipsec_fdb_tx_chk", ipsec_priv.ipsec_fdb_tx_chk)

uar = mlx5e_priv.mdev.priv.uar
print(uar)

net = prog['init_net']
netns_xfrm = net.xfrm

for x in list_for_each_entry('struct xfrm_state', netns_xfrm.state_all.address_of_(), 'km.all'):
    print(x.id)
    print(x.xso)
