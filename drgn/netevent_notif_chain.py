#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5_pf0()
esw = mlx5e_priv.mdev.priv.eswitch

netevent_notif_chain = prog['netevent_notif_chain']
notifier_block = netevent_notif_chain.head
while True:
    if notifier_block.value_() == 0:
        break
#     print(notifier_block)
    mlx5e_neigh_update_table = container_of(notifier_block, "struct mlx5e_neigh_update_table", "netevent_nb")
#     print(mlx5e_neigh_update_table)
    mlx5e_rep_priv = container_of(mlx5e_neigh_update_table, "struct mlx5e_rep_priv", "neigh_update")
    netdev = mlx5e_rep_priv.netdev.value_()
    if netdev:
        print("net_device %x, name: %s" % (mlx5e_rep_priv.netdev.value_(), mlx5e_rep_priv.netdev.name.string_().decode()))
    print(address_to_name(hex(notifier_block.notifier_call.value_())))
    notifier_block = notifier_block.next
    print('')
