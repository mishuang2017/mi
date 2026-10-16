#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn.helpers.linux.xarray import _xa_is_node
from drgn import Object
import time
import socket
import sys
import os
import enum

sys.path.append(".")
from lib import *

esw_manager_vport = 0

MLX5_NUM_TT = prog['MLX5_NUM_TT']

def print_port_sel(port_sel):
    print(port_sel)

    print('------port_sel start-------')
    mlx5_lag_definer = port_sel.outer.definers
    for i in range(MLX5_NUM_TT.value_()):
        if mlx5_lag_definer[i]:
            print("---------------------%d-----------------------\n" % i)
            print(mlx5_lag_definer[i].definer)
            flow_table("", mlx5_lag_definer[i].ft)
    print('------port_sel end-------')

MLX5_LAG_XA_MARK_MASTER = 1  # #define MLX5_LAG_XA_MARK_MASTER XA_MARK_1

def xa_marked_indices(xa, mark_bit):
    # xa_for_each() (drgn.helpers.linux.xarray) has no mark-aware variant, so
    # hand-walk the xa_node tree the same way it does internally, additionally
    # checking node->marks[mark_bit][0] (XA_MARK_LONGS == 1 on 64-bit, since
    # XA_CHUNK_SIZE == BITS_PER_LONG == 64) at each slot before yielding.
    # NOTE: does not handle the single-direct-entry case (xa_head itself is
    # the entry, no xa_node) -- irrelevant here since a LAG with a marked
    # master always has >=2 members and therefore a real xa_node.
    node_type = xa.prog_.type('struct xa_node *')

    def to_node(v):
        return Object(xa.prog_, node_type, v - 2)

    class _Node:
        def __init__(self, node, index):
            self.node = node
            self.index = index
            self.shift = node.shift.value_()
            self.next_slot = 0

    entry = xa.xa_head.read_()
    if not _xa_is_node(entry.value_()):
        return
    stack = [_Node(to_node(entry.value_()), 0)]
    while stack:
        n = stack[-1]
        if n.next_slot >= 64:
            stack.pop()
            continue
        slot = n.next_slot
        child = n.node.slots[slot].read_()
        cv = child.value_()
        index = n.index + (slot << n.shift)
        n.next_slot += 1
        if _xa_is_node(cv):
            stack.append(_Node(to_node(cv), index))
        elif cv != 0:
            marks_word = n.node.marks[mark_bit][0].value_()
            if (marks_word >> slot) & 1:
                yield index, child

def lag_member(address):
    # The per-member struct type name also varies: struct lag_func
    # (upstream) vs struct lag_fn (OFED "rename PF naming to fn" backport).
    for type_name in ('struct lag_func', 'struct lag_fn'):
        try:
            return Object(prog, type_name, address=address)
        except LookupError:
            continue
    raise LookupError("neither struct lag_func nor struct lag_fn found")

def print_master(mlx5_lag):
    members = get_lag_members(mlx5_lag)
    any_master = False
    for idx, entry in xa_marked_indices(members.address_of_(), MLX5_LAG_XA_MARK_MASTER):
        any_master = True
        lag_func = lag_member(entry.value_())
        pci_name = lag_func.dev.device.kobj.name.string_().decode()
        print("MLX5_LAG_XA_MARK_MASTER -> xa_idx: %d, pci: %s, lag_func.idx: %d" %
              (idx, pci_name, lag_func.idx.value_()))
    if not any_master:
        print("MLX5_LAG_XA_MARK_MASTER -> none marked")

def get_lag_members(mlx5_lag):
    # struct mlx5_lag's per-member xarray field name varies by tree/branch:
    #   pfs   -- original upstream name (LAG members are physical-port PFs)
    #   funcs -- upstream rename once virt-LAG allowed VF/SF members too
    #   fns   -- OFED backport's own rename (same intent, different name:
    #            "net/mlx5: LAG, rename PF naming to fn")
    # Try all three so this script works across cmi/linux and the OFED tree.
    for name in ('funcs', 'fns', 'pfs'):
        try:
            return getattr(mlx5_lag, name)
        except AttributeError:
            continue
    raise AttributeError("struct mlx5_lag has none of funcs/fns/pfs")

USER_PREF_MODE_NAMES = {
    0: "unset (driver auto-selects)",
    1: "queue_affinity",  # MLX5_LAG_USER_PREF_MODE_QUEUE_AFFINITY
    2: "hash",            # MLX5_LAG_USER_PREF_MODE_HASH
    3: "multiport_esw",   # MLX5_LAG_USER_PREF_MODE_MULTI_PORT_ESW
}

def lag_port_select_mode_str(lag_func):
    # fn->user_mode: OFED-only preference set via
    # /sys/class/net/<link>/compat/devlink/lag_port_select_mode
    # (mlx5_lag_set_user_mode()/MLX5_LAG_USER_PREF_MODE_*). 0 = unset.
    try:
        val = lag_func.user_mode.value_()
    except AttributeError:
        return "n/a (field not present in this tree)"
    return USER_PREF_MODE_NAMES.get(val, "unknown (%d)" % val)

def print_v2p_map(mlx5_lag):
    # ldev->v2p_map[member_idx * buckets + bucket_idx] = physical port that
    # bucket currently routes to (u8, 1-based port number). This is the
    # table mlx5_modify_lag()/_mlx5_modify_lag() reprograms into the FW
    # tx_remap_affinity_1/2 (or lagc ports array) fields on failover --
    # i.e. the actual live TX port-affinity steering state.
    buckets = mlx5_lag.buckets.value_()
    ports = mlx5_lag.ports.value_()
    v2p_map = mlx5_lag.v2p_map
    print("mlx5_lag.v2p_map %x (ports: %d, buckets: %d)" %
          (v2p_map.address_of_(), ports, buckets))
    if not v2p_map or buckets == 0:
        print("  (empty)")
        return
    for i in range(ports):
        row = [int(v2p_map[i * buckets + j]) for j in range(buckets)]
        print("  member[%d] buckets -> ports: %s" % (i, row))

def print_pfs(mlx5_lag):
    pfs = get_lag_members(mlx5_lag)
    # pf_metadata[] is only populated in MPESW mode (mlx5_mpesw_metadata_set);
    # it is a per-PF unique uplink source metadata (reg_c_0 >> 16).
    try:
        MLX5_LAG_MODE_MPESW = prog['MLX5_LAG_MODE_MPESW']
        is_mpesw = int(mlx5_lag.mode.value_()) == int(MLX5_LAG_MODE_MPESW.value_())
    except Exception:
        is_mpesw = False
    for node in radix_tree_for_each(pfs.address_of_()):
        lag_func = lag_member(node[1].value_())
        pci_name = lag_func.dev.device.kobj.name.string_().decode()
        idx = lag_func.idx.value_()
        print('---lag_func---')
        print("pci_name: %s, lag_func.idx: %d" % (pci_name, idx))
        print("  lag_port_select_mode: %s" % lag_port_select_mode_str(lag_func))
        if is_mpesw:
            pf_md = int(mlx5_lag.lag_mpesw.pf_metadata[idx].value_())
            print("  pf_metadata[%d]: 0x%x   (uplink reg_c_0 = 0x%x)" %
                  (idx, pf_md, (pf_md << 16) & 0xffffffff))
        else:
            print("  pf_metadata: n/a (not MPESW)")
#         print("lag_func.group_id: %d, lag_func.sd_fdb_active: %d" %
#             (lag_func.group_id.value_(), lag_func.sd_fdb_active.value_()))
#         print(lag_func)

# for name in pf0_name,pf1_name:
for name in pf0_name,:
    mlx5e_priv = get_mlx5e_priv(name)
    mlx5_lag = mlx5e_priv.mdev.priv.lag

    print('-------------')
    MLX5_LAG_MODE_ROCE = prog['MLX5_LAG_MODE_ROCE']
    MLX5_LAG_MODE_SRIOV = prog['MLX5_LAG_MODE_SRIOV']
    MLX5_LAG_MODE_MULTIPATH = prog['MLX5_LAG_MODE_MULTIPATH']

    print("MLX5_LAG_MODE_ROCE: %x" % MLX5_LAG_MODE_ROCE)
    print("MLX5_LAG_MODE_SRIOV: %x" % MLX5_LAG_MODE_SRIOV)
    print("MLX5_LAG_MODE_MULTIPATH: %x" % MLX5_LAG_MODE_MULTIPATH)

    print("mlx5_lag.mode_flags: %d" % mlx5_lag.mode_flags)
    print("mlx5_lag %x" % mlx5_lag.value_())
    print('-------------')
#     print("mode_flags: %x (MLX5_LAG_MODE_FLAG_SHARED_FDB: 2)" % mlx5_lag.mode_flags)
#     print("state_flags: %x (MLX5_LAG_MODE_NDEVS_READY = 1)" % mlx5_lag.state_flags)
#     print(mlx5_lag)
    print_v2p_map(mlx5_lag)
#     print(mlx5_lag.tracker)
    port_sel = mlx5_lag.port_sel
    print_port_sel(port_sel)
#     continue
#     print(mlx5_lag.pf[0])
#     print(mlx5_lag.pf[1])
    print("mlx5_lag.ports: %d" % mlx5_lag.ports)
    print_pfs(mlx5_lag)
    print_master(mlx5_lag)
    print("")
    print("mlx5_lag.mode: %s" % mlx5_lag.mode.format_())
#     print("mlx5_lag %x, flags: %x" % (mlx5_lag, mlx5_lag.flags))
#     print_fib_info(mlx5_lag.lag_mp.mfi)
    print('')
    esw = mlx5e_priv.mdev.priv.eswitch
    esw_manager_vport = esw.manager_vport
#     print("esw.manager_vport: %x" % esw_manager_vport)

# exit(0)

# if mlx5_lag.mode !=  MLX5_LAG_MODE_SRIOV:
#     exit(0)

def print_mlx5_vport(priv):
    mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
    vports = mlx5_eswitch.vports
    total_vports = mlx5_eswitch.total_vports
    enabled_vports = mlx5_eswitch.enabled_vports

    print("total_vports: %d" % total_vports)
    print("enabled_vports: %d" % enabled_vports)

    def print_vport(vport):
        if vport.vport != esw_manager_vport and vport.vport != 0xffff:
            return
        print(" ==== %s %x ====\n" % (priv.netdev.name.string_().decode(), vport.vport))
        print("mlx5_vport %x" % vport.address_of_(), end=' ')
        print("vport: %4x, metadata: %4x" % (vport.vport, vport.metadata), end=' ')
        print("\tdevlink_port %18x" % vport.dl_port.value_(), end=' ')
        print("vport: %5x" % vport.vport, end=' ')
        print("enabled: %x" % vport.enabled.value_(), end=' ')
        print('')

        # if egress acl is not NULL, it is shared_fdb
#         if vport.egress.acl:
#             flow_table("vport.egress.acl", vport.egress.acl)

#         print("vport.ingress.acl start")
#         if vport.ingress.acl:
#             flow_table("vport.ingress.acl", vport.ingress.acl)
#         print("vport.ingress.acl end")

    for node in radix_tree_for_each(vports.address_of_()):
        mlx5_vport = Object(prog, 'struct mlx5_vport', address=node[1].value_())
#         print_vport(mlx5_vport)

mlx5e_priv = get_mlx5_pf0()
print_mlx5_vport(mlx5e_priv)

# mlx5e_priv = get_mlx5_pf1()
# print_mlx5_vport(mlx5e_priv)
