#!/usr/local/bin/drgn -k
#
# Dump LAG demux rules (VF-LAG RX de-multiplex) -- the RX-side counterpart to
# peer_miss_rules.py.
#
#   ldev = mdev->priv.lag
#   for each lag_func in ldev->pfs (only the MASTER has lag_demux_fg populated):
#       master->lag_demux_ft / lag_demux_fg  : the demux flow table + group
#       master->lag_demux_rules              : xarray keyed by vport index/number,
#                                              value = struct mlx5_flow_handle *
#   each rule:  match reg_c_0 (a vport's src metadata) -> dest VHCA_RX vhca_id
#               (deliver received traffic to that vport's owning device's RX).
#
# Usage:  drgn -k lag_demux_rules.py [ifname]    (default: p0)
#
from drgn import Object, cast, FaultError, container_of
from drgn.helpers.linux import *
from socket import ntohl
import sys

IFNAME = sys.argv[1] if len(sys.argv) > 1 else "p0"

def pci_of(mdev):
    try:
        return mdev.pdev.dev.kobj.name.string_().decode()
    except Exception:
        return "?"

def vport_label(num):
    return {0x0: "HOST_PF", 0xfffe: "ECPF", 0xffff: "UPLINK"}.get(num, "VF/SF")

def const(name):
    try:
        return int(prog[name].value_())
    except Exception:
        return None

DEST_VHCA_RX = const('MLX5_FLOW_DESTINATION_TYPE_VHCA_RX')
DEST_VPORT   = const('MLX5_FLOW_DESTINATION_TYPE_VPORT')

def match_reg_c0(fh):
    try:
        fte = container_of(fh.rule[0].node.parent, 'struct fs_fte', 'node')
        return ntohl(int(fte.val[59].value_()) & 0xffffffff)   # misc2.metadata_reg_c_0
    except Exception:
        return None

def dest_str(fh):
    try:
        d = fh.rule[0].dest_attr
        t = int(d.type.value_())
        if DEST_VHCA_RX is not None and t == DEST_VHCA_RX:
            return "VHCA_RX vhca_id=%d" % int(d.vhca.id.value_())
        if DEST_VPORT is not None and t == DEST_VPORT:
            return "VPORT 0x%x vhca_id=%d" % (int(d.vport.num.value_()),
                                              int(d.vport.vhca_id.value_()))
        return "dest_type=%s" % str(d.type)
    except Exception as e:
        return "dest?(%s)" % e

# ---- resolve target netdev -> mdev -> ldev ----
nd = netdev_get_by_name(prog['init_net'], IFNAME)
if not nd:
    print("netdev %s not found" % IFNAME); sys.exit(1)
priv = netdev_priv(nd, "struct mlx5e_priv")
mdev = priv.mdev
ldev = mdev.priv.lag
if not ldev.value_():
    print("%s (%s): priv.lag = NULL -- not in a LAG" % (IFNAME, pci_of(mdev)))
    sys.exit(0)

print("=== LAG demux on %s  (mdev %s, ldev %#x, ports=%d, mode=%s) ==="
      % (IFNAME, pci_of(mdev), ldev.value_(), int(ldev.ports.value_()), str(ldev.mode)))

total = 0
found_master = False
for idx, ent in xa_for_each(ldev.pfs.address_of_()):
    pf = cast('struct lag_func *', ent)
    if not pf.lag_demux_fg.value_():
        continue                       # demux resources only on the master
    found_master = True
    ft = pf.lag_demux_ft
    ftid = int(ft.id.value_()) if ft.value_() else 0
    print("\n-- MASTER lag_func idx=%d dev=%s  demux_ft=%#x (id=0x%x)  demux_fg=%#x --"
          % (int(idx), pci_of(pf.dev), ft.value_(), ftid, pf.lag_demux_fg.value_()))
    cnt = 0
    for vport, rule in xa_for_each(pf.lag_demux_rules.address_of_()):
        try:
            fh = cast('struct mlx5_flow_handle *', rule)
            vport = int(vport)
            regc0 = match_reg_c0(fh)
            rc = ("reg_c0=0x%x" % regc0) if regc0 is not None else "reg_c0=?"
            print("   vport 0x%-4x (%-7s)  rule %#x  match %-16s -> %s"
                  % (vport, vport_label(vport), fh.value_(), rc, dest_str(fh)))
            cnt += 1; total += 1
        except FaultError as e:
            print("   [key %s] <fault: %s>" % (vport, e))
    print("   (%d demux rules)" % cnt)

if not found_master:
    print("\n(no master lag_func with demux resources -- not a VF-LAG master, "
          "or demux not set up here)")
print("\nTOTAL LAG demux rules: %d" % total)
