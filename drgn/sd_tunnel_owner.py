#!/usr/local/bin/drgn -k
#
# CT ingress-leak probe for BF4 MPESW shared-FDB (0002 master / 0006 non-master).
#
# For each uplink netdev it prints:
#   1. SD state       -> mlx5_sd_get_primary() equivalent (sd->primary / primary_dev)
#   2. LAG/MPESW state-> lag mode, SHARED_FDB flag, and every bonded peer dev
#   3. uplink_priv    -> tunnel_mapping owner + per-uplink ct_priv CT-offload counts
#
# Backend-independent CT accounting via ct_priv rhashtables (works for dmfs/smfs/hmfs):
#   tuples_ht / tuples_nat_ht = learned established tuples ; zone_ht = active CT zones.
#
# Usage:  drgn -k sd_tunnel_owner.py [ifname ...]     (default: p0 p1)
#   Run it BOTH in the working and the leaking state and diff the SUMMARY block.
#   Hypothesis: in the leaking state the non-master (p1) shows FEWER tuples than p0.
#
from drgn import Object, cast
from drgn.helpers.linux import *
import sys

NETDEV_ALIGN = 32
SHARED_FDB_BIT = 1          # enum MLX5_LAG_MODE_FLAG_SHARED_FDB
IFNAMES = sys.argv[1:] if len(sys.argv) > 1 else ["p0", "p1"]

def find_netdev(name):
    for nd in for_each_netdev(prog["init_net"]):
        try:
            if nd.name.string_().decode() == name:
                return nd
        except Exception:
            continue
    return None

def netdev_priv(dev):
    sz = prog.type('struct net_device').size
    off = (sz + NETDEV_ALIGN - 1) & ~(NETDEV_ALIGN - 1)
    return dev.value_() + off

def pci_of(mdev):
    try:
        return mdev.pdev.dev.kobj.name.string_().decode()
    except Exception:
        return "?"

def nelems(rh):
    try:
        return rh.nelems.counter.value_()
    except Exception:
        return None

def probe(IFNAME):
    dev = find_netdev(IFNAME)
    if dev is None or not dev.value_():
        print("netdev %s not found" % IFNAME); return None

    priv = Object(prog, 'struct mlx5e_priv', address=netdev_priv(dev))
    mdev = priv.mdev
    pci = pci_of(mdev)
    print("=== netdev %s -> mdev %#x  (pci %s) ===" % (IFNAME, mdev.value_(), pci))

    # -------------------------------------------------------------- 1. SD state
    sd = mdev.sd
    if not sd.value_():
        print("[SD ] mdev->sd = NULL  -> mlx5_sd_get_primary() returns dev itself (no SD anchor)")
    else:
        is_primary = bool(sd.primary)
        print("[SD ] sd %#x  group_id=%d  state=%d  primary=%s"
              % (sd.value_(), sd.group_id.value_(), sd.state.value_(), is_primary))
        if is_primary:
            print("      mlx5_sd_get_primary() -> THIS dev (%s) is the SD primary" % pci)
        else:
            pdev = sd.primary_dev
            print("      mlx5_sd_get_primary() -> primary_dev %#x (pci %s)  <== master anchor"
                  % (pdev.value_(), pci_of(pdev)))

    # ----------------------------------------------------------- 2. LAG / MPESW
    lag = mdev.priv.lag
    if not lag.value_():
        print("[LAG] priv.lag = NULL  (not bonded)")
    else:
        flags = lag.mode_flags.value_()
        shared = bool(flags & (1 << SHARED_FDB_BIT))
        print("[LAG] lag %#x  mode=%s  mode_flags=%#x  SHARED_FDB=%s  ports=%d"
              % (lag.value_(), str(lag.mode), flags, shared, lag.ports.value_()))
        try:
            for idx, ent in xa_for_each(lag.pfs.address_of_()):
                pf = cast('struct lag_func *', ent)
                fdev = pf.dev
                if not fdev.value_():
                    continue
                nd = pf.netdev
                ndn = ""
                try:
                    if nd.value_():
                        ndn = nd.name.string_().decode()
                except Exception:
                    pass
                print("      pf[idx=%d] dev %#x (pci %s) netdev=%s group_id=%d sd_fdb_active=%s"
                      % (idx, fdev.value_(), pci_of(fdev), ndn,
                         pf.group_id.value_(), bool(pf.sd_fdb_active)))
        except Exception as e:
            print("      (could not walk lag.pfs: %s)" % e)

    # --------------------------------------------------- 3. uplink_priv CT ctx
    counts = None
    rpriv = cast('struct mlx5e_rep_priv *', priv.ppriv)
    up = rpriv.uplink_priv
    try:
        tm = up.tunnel_mapping
        ct = up.ct_priv
        print("[UP ] uplink_priv %#x  tunnel_mapping=%#x  ct_priv=%#x"
              % (up.address_of_().value_(), tm.value_(), ct.value_()))
        if ct.value_():
            cft = ct.ct; nft = ct.ct_nat
            print("      ct     FT %#x  id=0x%x  level=%d" % (cft.value_(), cft.id.value_(), cft.level.value_()))
            print("      ct_nat FT %#x  id=0x%x  level=%d" % (nft.value_(), nft.id.value_(), nft.level.value_()))
            t  = nelems(ct.ct_tuples_ht)
            tn = nelems(ct.ct_tuples_nat_ht)
            z  = nelems(ct.zone_ht)
            print("      tuples_ht=%s  tuples_nat_ht=%s  zone_ht=%s" % (t, tn, z))
            counts = (t, tn, z)
    except Exception as e:
        print("      (uplink_priv read failed: %s)" % e)
    return (IFNAME, pci, counts)

rows = []
for name in IFNAMES:
    r = probe(name)
    if r:
        rows.append(r)
    print("")

# ------------------------------------------------------------------- SUMMARY
print("================= SUMMARY (CT offload per uplink) =================")
print("%-6s %-16s %10s %14s %8s" % ("ifname", "pci", "tuples", "tuples_nat", "zones"))
for name, pci, c in rows:
    if c is None:
        print("%-6s %-16s   <no ct_priv / read failed>" % (name, pci))
    else:
        print("%-6s %-16s %10s %14s %8s" % (name, pci, c[0], c[1], c[2]))
if len(rows) == 2 and rows[0][2] and rows[1][2]:
    a, b = rows[0][2][0], rows[1][2][0]
    if a is not None and b is not None:
        if a == b:
            print(">> tuples SYMMETRIC (%s==%s): CT learning mirrored to both uplinks." % (a, b))
            print("   If it still leaks, the miss is upstream of CT (decap->goto-CT wiring or pre-CT match).")
        else:
            lo = rows[0] if a < b else rows[1]
            print(">> tuples ASYMMETRIC: %s has FEWER (%d vs %d) -> CT NOT mirrored to that uplink."
                  % (lo[0], min(a, b), max(a, b)))
            print("   That closes it: driver bug, CT connection offloaded only on the other PF.")
