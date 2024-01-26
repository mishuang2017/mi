#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

import sys
import os

sys.path.append("..")
# from lib import *
from lib_pedit import *

mlx5e_rep_priv = get_mlx5e_rep_priv()
ct_priv = mlx5e_rep_priv.uplink_priv.ct_priv
# print(ct_priv)
# tunnel_mapping = mlx5e_rep_priv.uplink_priv.tunnel_mapping
# labels_mapping = ct_priv.labels_mapping
# zone_mapping = ct_priv.zone_mapping

# print(ct_priv.debugfs)

# print(ct_priv.dev.priv.dbg.dbg_root)

# exit(0)
print("\n=== mlx5e_rep_priv.uplink_priv.ct_priv.zone_ht ===")
zone_ht = ct_priv.zone_ht
# print(zone_ht)

for i, mlx5_ct_ft in enumerate(hash(zone_ht, 'struct mlx5_ct_ft', 'node')):
    print("mlx5_ct_ft.ct_entries_ht:")
    ct_entries_ht = mlx5_ct_ft.ct_entries_ht
    for j, mlx5_ct_entry in enumerate(hash(ct_entries_ht, 'struct mlx5_ct_entry', 'node')):
        print("mlx5_ct_entry %lx" % mlx5_ct_entry)
#         print("\tcookie is flow_offload_tuple %lx" % mlx5_ct_entry.cookie)
#         print("\trestore_cookie is 'ct | ctinfo' %lx" % mlx5_ct_entry.restore_cookie)
#         print('')
