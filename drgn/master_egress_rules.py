#!/usr/local/bin/drgn -k
#
# Dump the eswitch MASTER manager-vport EGRESS ACL + bounce rules
# (shared-FDB LAG / MPESW / Socket-Direct).
#
#   esw->manager_vport                          : the manager vport number (ECPF/PF/VF)
#   vport = esw->vports[manager_vport]
#     vport->egress.acl                         : the egress ACL flow table (or NULL)
#     vport->egress.type                        : DEFAULT / SHARED_FDB
#     vport->egress.offloads.fwd_rule           : single fwd2vport rule (rep-bond path)
#     vport->egress.offloads.bounce_rules       : xarray keyed by SLAVE vhca_id
#         value = struct mlx5_flow_handle *  ->  match (source_port==UPLINK &&
#                 source_eswitch_owner_vhca_id==slave)  ->  fwd to slave manager vport
#
# These "bounce rules" are created by __esw_set_master_egress_rule() during
# mlx5_lag_shared_fdb_create(); they redirect each slave-uplink-sourced packet
# to that slave's own manager vport. On a plain (non-LAG-master) uplink there is
# NO egress ACL at all (esw_acl_egress_needed() is VF/SF only).
#
# Usage:  drgn -k master_egress_rules.py [ifname]   (default: p0; run per uplink)
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

def egress_type_str(vport):
    try:
        return str(vport.egress.type)
    except Exception:
        return "?"

# ---- find target netdev + its eswitch (same helpers as peer_miss_rules.py) ----
target_nd = netdev_get_by_name(prog['init_net'], IFNAME)
if not target_nd:
    print("netdev %s not found" % IFNAME); sys.exit(1)

t_priv = netdev_priv(target_nd, "struct mlx5e_priv")
t_mdev = t_priv.mdev
t_esw = t_mdev.priv.eswitch
if not t_esw.value_():
    print("netdev %s: mdev=%#x has NULL eswitch (not switchdev)" % (IFNAME, t_mdev.value_()))
    sys.exit(1)

t_vid = dev_vhca_id(t_mdev)
try:
    mgr = int(t_esw.manager_vport.value_())
except Exception:
    mgr = -1
print("=== master egress on %s  (esw %#x, vhca_id %d, manager_vport 0x%x) ==="
      % (pci_of(t_mdev), t_esw.value_(), t_vid, mgr))

# ---- best-effort: vhca_id -> (mdev, esw) for slave labels ----
vhca_map = {}
for nd in list_for_each_entry('struct net_device',
                              prog['init_net'].dev_base_head.address_of_(), 'dev_list'):
    try:
        if "mlx5e" not in sym(nd.netdev_ops.value_()):
            continue
        p = netdev_priv(nd, "struct mlx5e_priv")
        e = p.mdev.priv.eswitch
        if e.value_():
            vhca_map[dev_vhca_id(p.mdev)] = p.mdev
    except Exception:
        continue

# ---- locate the manager vport struct ----
mgr_vport = None
try:
    for vnum, vp in xa_for_each(t_esw.vports.address_of_()):
        if int(vnum) == mgr:
            mgr_vport = cast('struct mlx5_vport *', vp)
            break
except Exception as e:
    print("  <failed to walk esw->vports: %s>" % e)

if mgr_vport is None:
    print("  manager vport 0x%x not found in esw->vports" % mgr); sys.exit(1)

# ---- UPLINK vport source metadata (what ingress stamps into reg_c_0) ----
# reg_c_0 = vport->metadata << (32 - ESW_SOURCE_PORT_METADATA_BITS); BITS = 16
UPLINK = 0xffff
try:
    up_vport = None
    for vnum, vp in xa_for_each(t_esw.vports.address_of_()):
        if (int(vnum) & 0xffff) == UPLINK:
            up_vport = cast('struct mlx5_vport *', vp)
            break
    if up_vport is not None:
        md  = int(up_vport.metadata.value_())
        dmd = int(up_vport.default_metadata.value_())
        print("  UPLINK vport metadata     : metadata=0x%x default_metadata=0x%x"
              "  => reg_c_0 match should be 0x%x" % (md, dmd, (md << 16) & 0xffffffff))
        if md != dmd:
            print("      NOTE: metadata != default_metadata (uplink was reassigned,"
                  " e.g. MPESW ingress-metadata-update)")
    else:
        print("  UPLINK vport metadata     : UPLINK vport not found")
except Exception as e:
    print("  UPLINK vport metadata     : <error: %s>" % e)

eg = mgr_vport.egress
acl = eg.acl
print("  egress.acl                : %s   type=%s"
      % (("ft %#x id=0x%x" % (acl.value_(), int(acl.id.value_()))) if acl.value_() else "NULL",
         egress_type_str(mgr_vport)))

# fwd_rule (single, rep-bond fwd2vport)
try:
    fr = eg.offloads.fwd_rule
    print("  egress.offloads.fwd_rule  : %s" % (("%#x" % fr.value_()) if fr.value_() else "NULL"))
except Exception as e:
    print("  egress.offloads.fwd_rule  : <n/a: %s>" % e)

def decode_match(fh):
    try:
        fte = container_of(fh.rule[0].node.parent, 'struct fs_fte', 'node')
        v17 = ntohl(int(fte.val[17].value_()) & 0xffffffff)   # misc: owner_vhca | source_port
        regc0 = ntohl(int(fte.val[59].value_()) & 0xffffffff) # misc2: metadata_reg_c_0
        sport = v17 & 0xffff
        owner = (v17 >> 16) & 0xffff
        # show BOTH so we can tell source_port-match vs reg_c_0-match apart
        try:
            grp = container_of(fte.node.parent, 'struct mlx5_flow_group', 'node')
            mce = int(grp.mask.match_criteria_enable.value_())
        except Exception:
            mce = -1
        return ("criteria_enable=0x%x source_port=0x%x(%s) owner_vhca_id=%d reg_c0=0x%x"
                % (mce, sport, vport_label(sport), owner, regc0))
    except Exception as e:
        return "match?(%s)" % e

def decode_dest(fh):
    try:
        d = fh.rule[0].dest_attr
        return "dest vport 0x%x vhca_id=%d" % (int(d.vport.num.value_()),
                                               int(d.vport.vhca_id.value_()))
    except Exception as e:
        return "dest?(%s)" % e

# bounce_rules xarray: key = slave vhca_id -> flow handle
print("  egress.offloads.bounce_rules :")
n = 0
try:
    for slave_vhca, rule in xa_for_each(eg.offloads.bounce_rules.address_of_()):
        slave_vhca = int(slave_vhca)
        fh = cast('struct mlx5_flow_handle *', rule)
        smdev = vhca_map.get(slave_vhca)
        spci = pci_of(smdev) if smdev is not None else "?"
        print("     slave vhca_id=%-3d (pci %-14s) rule %#x  %-42s -> %s"
              % (slave_vhca, spci, fh.value_(), decode_match(fh), decode_dest(fh)))
        n += 1
except FaultError as e:
    print("     <fault walking bounce_rules: %s>" % e)
except Exception as e:
    print("     <bounce_rules unavailable: %s>" % e)

print("  (%d bounce rule(s))" % n)
if n == 0 and acl.value_():
    print("  NOTE: egress ACL exists but no bounce rules -- expected if this uplink")
    print("        is not the shared-FDB LAG master, or rules not (yet) installed.")
