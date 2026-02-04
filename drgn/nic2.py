#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

# /* NIC prio FTS */
# enum {
# 0        MLX5E_PROMISC_FT_LEVEL,
# 57        MLX5E_VLAN_FT_LEVEL,
# 58        MLX5E_L2_FT_LEVEL,
# 59        MLX5E_TTC_FT_LEVEL,
# 69        MLX5E_INNER_TTC_FT_LEVEL,
# 0        MLX5E_FS_TT_UDP_FT_LEVEL = MLX5E_INNER_TTC_FT_LEVEL + 1,
# 0        MLX5E_FS_TT_ANY_FT_LEVEL = MLX5E_INNER_TTC_FT_LEVEL + 1,
#ifdef CONFIG_MLX5_EN_TLS
#         MLX5E_ACCEL_FS_TCP_FT_LEVEL = MLX5E_INNER_TTC_FT_LEVEL + 1,
#endif
#ifdef CONFIG_MLX5_EN_ARFS
# 0        MLX5E_ARFS_FT_LEVEL = MLX5E_INNER_TTC_FT_LEVEL + 1,
#endif
#ifdef CONFIG_MLX5_EN_IPSEC
#         MLX5E_ACCEL_FS_ESP_FT_LEVEL = MLX5E_INNER_TTC_FT_LEVEL + 1,
#         MLX5E_ACCEL_FS_ESP_FT_ERR_LEVEL,
#         MLX5E_ACCEL_FS_POL_FT_LEVEL,
#         MLX5E_ACCEL_FS_ESP_FT_ROCE_LEVEL,
#endif
# };

print_mlx5e_tc_flow_flags()

for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    addr = dev.value_()
    if name != "enp8s0f0":
        continue;
    print(name)

    mlx5e_priv = get_mlx5(dev)

    print(name)
    print(dev.name)

    fs = mlx5e_priv.fs
#     print(fs)
#     flow_table("l2", fs.l2.ft.t)
    flow_table("ttc", fs.ttc.t)
    print(fs.ttc.groups)
    continue
    print(fs.udp)
#     print(fs.arfs)
    for i in range(4):
        flow_table("arfs", fs.arfs.arfs_tables[i].ft.t)
#     print(fs.ethtool)
#     for i in range(4):
#         print(fs.ethtool.l2_ft[i])
#     for i in range(7):
#         print(fs.ethtool.l3_l4_ft[i])
    flow_table("inner_ttc", fs.inner_ttc.t)
    flow_table("vlan", fs.vlan.ft.t)
