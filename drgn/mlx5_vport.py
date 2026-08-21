#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

# print esw->vports, struct mlx5_vport

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

def print_mac(mac):
    print("mac: %02x:%02x:%02x:%02x:%02x:%02x" % (mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]), end=' ')

def bswap32(x):
    x &= 0xffffffff
    return ((x & 0xff) << 24) | ((x & 0xff00) << 8) | ((x >> 8) & 0xff00) | ((x >> 24) & 0xff)

def pci_of(mdev):
    try:
        return mdev.pdev.dev.kobj.name.string_().decode()
    except Exception:
        return "?"

def dev_vhca_id(mdev):
    # MLX5_CAP_GEN(mdev, vhca_id): cmd_hca_cap is stored big-endian; vhca_id is
    # bits [48:63] -> low 16 bits of dword 1 after be32->cpu. MLX5_CAP_GENERAL = 0.
    try:
        cur = mdev.caps.hca[0].cur
        return "%d" % (bswap32(cur[1].value_()) & 0xffff)
    except Exception as e:
        return "?(%s)" % e

def print_mlx5_vport(priv):
    mlx5_eswitch = priv.mdev.priv.eswitch
    print("=== PF %s   device vhca_id: %s (== flow-dest 'vhca_id') ===" %
          (pci_of(priv.mdev), dev_vhca_id(priv.mdev)))
    vports = mlx5_eswitch.vports
    total_vports = mlx5_eswitch.total_vports
    enabled_vports = mlx5_eswitch.enabled_vports

    print("total_vports: %d" % total_vports)
    print("enabled_vports: %d" % enabled_vports)

    uplink_idx = total_vports - 1
    # uplink_vport = vports[uplink_idx]
    # print(vports)

    def print_vport(vport):
        print("mlx5_vport %x" % vport.address_of_(), end=' ')
        print("vport: %4x, metadata: %4x, index: %4x" % (vport.vport, vport.metadata, vport.index), end=' ')
#         print(vport.info.link_state)
        print_mac(vport.info.mac)
#         print("fw_pages: %8d" % vport.fw_pages, end=' ')
#         print(vport.qos.sched_node)
#         print("\tdevlink_port %18x" % vport.dl_port.value_(), end=' ')
#         if vport.dl_port:
#             print(vport.dl_port.devlink_rate)
        print("enabled: %x" % vport.enabled, end=' ')
        # per-vport vhca_id field (owner vhca for delegated/proxy vports; often 0/-1 for local)
        try:
            print("vport.vhca_id: %d" % vport.vhca_id, end=' ')
        except Exception:
            pass
#         if vport.enabled:
#             print(vport)
#             print(vport.dl_port)
#         print("vlan: %d" % vport.info.vlan, end=' ')
#         print("vhca_id: %d" % vport.vhca_id, end=' ')
#         if vport.ingress.acl:
#             lib.flow_table("ingress", vport.ingress.acl)
#         if vport.egress.acl:
#             lib.flow_table("egress", vport.egress.acl)
#             print(vport.ingress.allow_rule)
        print('')

    # for i in range(enabled_vports):
    #     print_vport(vports[i])

    # uplink_devlink_port = mlx5e_priv.mdev.mlx5e_res.dl_port
    # print("uplink:\n\tdevlink_port %x" % uplink_devlink_port.address_of_())
    # print_vport(uplink_vport)
    # print(mlx5e_priv.mdev.mlx5e_res)

    for node in radix_tree_for_each(vports.address_of_()):
        mlx5_vport = Object(prog, 'struct mlx5_vport', address=node[1].value_())
#         print(mlx5_vport.info)
#         if mlx5_vport.vport != 0xffff:
#             continue
        print_vport(mlx5_vport)
#         print(mlx5_vport.ingress.offloads)

mlx5e_priv = lib.get_mlx5_pf0()
print_mlx5_vport(mlx5e_priv)
mlx5e_priv = lib.get_mlx5_pf1()
print_mlx5_vport(mlx5e_priv)
