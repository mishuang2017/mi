#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

def bswap32(x):
    x &= 0xffffffff
    return ((x & 0xff) << 24) | ((x & 0xff00) << 8) | ((x >> 8) & 0xff00) | ((x >> 24) & 0xff)

def dev_vhca_id(mdev):
    # MLX5_CAP_GEN(mdev, vhca_id): cmd_hca_cap stored big-endian; vhca_id is
    # bits[48:63] -> low 16 bits of dword 1 after be32->cpu. MLX5_CAP_GENERAL = 0.
    try:
        return "%d" % (bswap32(mdev.caps.hca[0].cur[1].value_()) & 0xffff)
    except Exception as e:
        return "?(%s)" % e

def pci_of(mdev):
    try:
        return mdev.pdev.dev.kobj.name.string_().decode()
    except Exception:
        return "?"

def eswitch_manager(mdev):
    # MLX5_CAP_GEN(mdev, eswitch_manager): cmd_hca_cap bit_off 423 (hand
    # counted from mlx5_ifc.h, anchored at reserved_at_16e=0x16e=366)
    # -> dword 13 (423//32), bit 24 (32-1-(423%32)) of that dword after
    # be32->cpu, same convention as dev_vhca_id() above.
    try:
        return bool((bswap32(mdev.caps.hca[0].cur[13].value_()) >> 24) & 0x1)
    except Exception as e:
        return "?(%s)" % e

vhca_map = []   # (netdev_name, pci, vhca_id) for the summary at the end

for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    addr = dev.value_()
#     print(dev.netdev_ops)
    ops = address_to_name(hex(dev.netdev_ops))
    if "mlx5e" not in ops:
        continue;
#     if name not in "en8f0pf0sf1":
#         continue;
#     if name not in "enp8s0f0":
#         continue;
    print("===================================================")
    print(name)
    print(dev.netdev_ops.ndo_get_port_parent_id)

    print("dev.num_tc: %d" % dev.num_tc)
    print(dev.tc_to_txq)
    print("dev.real_num_tx_queues: %d" % dev.real_num_tx_queues)
#     print(dev.ethtool_ops)
#     print(dev.dcbnl_ops)

#     if dev.devlink_port:
#         dl_port = dev.devlink_port
#         for i in range(dl_port.attrs.switch_id.id_len):
#             print("%02x:" % dl_port.attrs.switch_id.id[i], end='')
#         print('')

    mlx5e_priv_addr = addr + prog.type('struct net_device').size
    mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)
    mdev = mlx5e_priv.mdev
    vid = dev_vhca_id(mdev)
    pci = pci_of(mdev)
    embedded_cpu = bool(mdev.caps.embedded_cpu.value_())
    esw_mgr = eswitch_manager(mdev)
    print("pci: %s   vhca_id: %s   (flow-dest 'vhca_id')   embedded_cpu: %s   eswitch_manager: %s" % (
        pci, vid, embedded_cpu, esw_mgr))
    vhca_map.append((name, pci, vid, embedded_cpu, esw_mgr))
#     print(mlx5e_priv.aso)
#     print("wq: %x" % mlx5e_priv.wq)
#     print(mlx5e_priv.ipsec)
#     print(mlx5e_priv.vhca_id)
#     print(mlx5e_priv.fs.tc.netdevice_nb.notifier_call)
#     print("mlx5e_priv_addr: %x" % mlx5e_priv_addr)
#     print(mlx5e_priv)
#     print(mlx5e_priv.init)
#     print(mlx5e_priv.fs.vlan_strip_disable)
#     if name in "enp8s0f0":
#             print(dev.page_pools)
#             for pool in hlist_for_each_entry('struct page_pool', dev.page_pools.address_of_(), 'user.list'):
#                 print(pool.alloc)
#         print("yes")
#         print(mlx5e_priv.channels.params.mqprio)

#     ppriv = mlx5e_priv.ppriv
#     if ppriv:
#         print("ppriv %lx" % ppriv.value_())
#         mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())
#     print(mlx5e_priv.profile)

    print('\t', end='')
    print('')

print("\n================= netdev -> vhca_id map =================")
print("%-20s %-16s %-8s %-13s %s" % ("netdev", "pci", "vhca_id", "embedded_cpu", "eswitch_manager"))
for name, pci, vid, embedded_cpu, esw_mgr in sorted(vhca_map, key=lambda r: r[2]):
    print("%-20s %-16s %-8s %-13s %s" % (name, pci, vid, embedded_cpu, esw_mgr))
