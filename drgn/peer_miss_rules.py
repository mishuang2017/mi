#!/usr/local/bin/drgn -k
#
# Dump eswitch FDB *peer miss rules* (shared-FDB / merged eswitch / MPESW / SD).
#
#   esw->fdb_table.offloads.peer_miss_rules : xarray
#       key   = peer device vhca_id
#       value = struct mlx5_flow_handle **flows   (len = peer_esw->total_vports,
#                                                   indexed by peer vport->index)
#   flows[i] = the miss rule matching that peer source-vport; it forwards to the
#              peer eswitch's manager vport (dest vport.num / vport.vhca_id).
#
# Usage:  drgn -k peer_miss_rules.py [ifname]     (default: p0; run per uplink)
#
from drgn import Object, cast, FaultError, container_of
from drgn.helpers.linux import *
from socket import ntohl
import sys

IFNAME = sys.argv[1] if len(sys.argv) > 1 else "p0"

def bswap32(x):
    x &= 0xffffffff
    return ((x & 0xff) << 24) | ((x & 0xff00) << 8) | ((x >> 8) & 0xff00) | ((x >> 24) & 0xff)

def dev_vhca_id(mdev):
    try:
        return bswap32(mdev.caps.hca[0].cur[1].value_()) & 0xffff   # MLX5_CAP_GEN(mdev, vhca_id)
    except Exception:
        return -1

def pci_of(mdev):
    try:
        return mdev.pdev.dev.kobj.name.string_().decode()
    except Exception:
        return "?"

def sym(addr):
    try:
        return prog.symbol(addr).name
    except Exception:
        return ""

def vport_label(num):
    return {0x0: "HOST_PF", 0xfffe: "ECPF", 0xffff: "UPLINK"}.get(num, "VF/SF")

# ---- find target netdev + its eswitch (use drgn's own helpers, like lib.py) ----
target_nd = netdev_get_by_name(prog['init_net'], IFNAME)
if not target_nd:
    names = [nd.name.string_().decode()
             for nd in list_for_each_entry('struct net_device',
                                            prog['init_net'].dev_base_head.address_of_(),
                                            'dev_list')]
    print("netdev %s not found. available: %s" % (IFNAME, ", ".join(names)))
    sys.exit(1)

t_priv = netdev_priv(target_nd, "struct mlx5e_priv")
t_mdev = t_priv.mdev
t_esw = t_mdev.priv.eswitch
if not t_esw.value_():
    print("netdev %s: mdev=%#x has NULL eswitch (not switchdev / not an eswitch netdev)"
          % (IFNAME, t_mdev.value_()))
    sys.exit(1)
t_vid = dev_vhca_id(t_mdev)
print("=== peer_miss_rules on %s  (esw %#x, vhca_id %d) ===" %
      (pci_of(t_mdev), t_esw.value_(), t_vid))

# ---- best-effort: vhca_id -> (mdev, esw) for peer names + vport labels ----
vhca_map = {}
for nd in list_for_each_entry('struct net_device',
                              prog['init_net'].dev_base_head.address_of_(), 'dev_list'):
    try:
        if "mlx5e" not in sym(nd.netdev_ops.value_()):
            continue
        p = netdev_priv(nd, "struct mlx5e_priv")
        e = p.mdev.priv.eswitch
        if e.value_():
            vhca_map[dev_vhca_id(p.mdev)] = (p.mdev, e)
    except Exception:
        continue

def vport_index_map(esw):
    """peer vport->index  ->  vport number, to label each flows[] slot."""
    m = {}
    try:
        for vnum, vp in xa_for_each(esw.vports.address_of_()):
            vpo = cast('struct mlx5_vport *', vp)
            m[int(vpo.index.value_())] = int(vpo.vport.value_())
    except Exception:
        pass
    return m

pm = t_esw.fdb_table.offloads.peer_miss_rules
total = 0
any_peer = False
for vhca_id, flows_val in xa_for_each(pm.address_of_()):
    any_peer = True
    vhca_id = int(vhca_id)
    flows = cast('struct mlx5_flow_handle **', flows_val)
    peer = vhca_map.get(vhca_id)
    if peer:
        n = int(peer[1].total_vports.value_())
        peer_pci = pci_of(peer[0])
        idx2vp = vport_index_map(peer[1])
    else:
        n = int(t_esw.total_vports.value_())    # fallback bound
        peer_pci = "?"
        idx2vp = {}
    print("\n-- peer vhca_id=%d (pci %s)  flows=%#x  slots=%d --"
          % (vhca_id, peer_pci, flows.value_(), n))
    cnt = 0
    for i in range(n):
        try:
            fh = flows[i]
        except FaultError:
            break
        if not fh.value_():
            continue
        cnt += 1; total += 1
        try:
            nr = int(fh.num_rules.value_())
            d = fh.rule[0].dest_attr
            dvp = int(d.vport.num.value_())
            dvh = int(d.vport.vhca_id.value_())
        except Exception:
            nr, dvp, dvh = -1, -1, -1
        # --- MATCH: navigate rule[0] -> fte -> group; read source-vport match ---
        try:
            fte = container_of(fh.rule[0].node.parent, 'struct fs_fte', 'node')
            grp = container_of(fte.node.parent, 'struct mlx5_flow_group', 'node')
            mce = int(grp.mask.match_criteria_enable.value_())
            v17 = ntohl(int(fte.val[17].value_()) & 0xffffffff)   # misc: owner_vhca | source_port
            regc0 = ntohl(int(fte.val[59].value_()) & 0xffffffff) # misc2: metadata_reg_c_0
            sport = v17 & 0xffff
            owner = (v17 >> 16) & 0xffff
            if mce & 0x8:        # MLX5_MATCH_MISC_PARAMETERS_2 -> metadata mode
                m = "match reg_c0=0x%x" % regc0
            elif mce & 0x2:      # MLX5_MATCH_MISC_PARAMETERS -> legacy mode
                m = "match source_port=0x%x owner_vhca_id=%d" % (sport, owner)
            else:
                m = "match criteria_enable=0x%x reg_c0=0x%x" % (mce, regc0)
        except Exception as e:
            m = "match?(%s)" % e
        src = idx2vp.get(i)
        srcs = ("src vport 0x%-4x (%s)" % (src, vport_label(src))) if src is not None else ("slot %d" % i)
        print("   [idx %3d] %-24s %-34s flow %#x  -> dest vport 0x%x vhca_id=%d"
              % (i, srcs, m, fh.value_(), dvp, dvh))
    print("   (%d miss rules for this peer)" % cnt)

if not any_peer:
    print("  (no peers paired -- peer_miss_rules xarray is empty)")
print("\nTOTAL peer miss rules across all peers: %d" % total)
