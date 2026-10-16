#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

import sys
import os

sys.path.append(".")
from lib import *

# struct mlx5e_resources.hw_objs (include/linux/mlx5/driver.h) is a per-mdev
# resource created once at netdev probe/resume (mlx5e_create_tises(), see
# en_common.c), not per-channel. Each TIS is created with
# lag_tx_port_affinity = lag_port + 1 baked into its HW context at creation
# time (en_common.c:mlx5e_create_tises()); that value is sent to FW only and
# not mirrored back into kernel memory, so we print the inferred affinity
# (lag_port + 1) alongside the TIS number rather than reading it back.

uplink = sys.argv[1] if len(sys.argv) > 1 else None
mlx5e_priv = get_mlx5e_priv(uplink) if uplink else get_mlx5_pf0()
mdev = mlx5e_priv.mdev

hw_objs = mdev.mlx5e_res.hw_objs

print("=== mdev.mlx5e_res.hw_objs ===")
print("pdn: %d" % hw_objs.pdn)
print("tdn: %d" % hw_objs.td.tdn)
print("mkey: %#x" % hw_objs.mkey)
print("num_bfregs: %d" % hw_objs.num_bfregs)
print("tisn_valid: %d" % bool(hw_objs.tisn_valid))

tisn = hw_objs.tisn
num_ports = len(tisn)
num_tc = len(tisn[0])

print("\n=== tisn[lag_port][tc] (lag_tx_port_affinity = lag_port + 1) ===")
for lag_port in range(num_ports):
    for tc in range(num_tc):
        tisn_val = int(tisn[lag_port][tc])
        if tisn_val == 0:
            continue
        print("lag_port: %d (affinity: %d)  tc: %d  tisn: %#x (%d)" %
              (lag_port, lag_port + 1, tc, tisn_val, tisn_val))
