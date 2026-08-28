#!/usr/local/bin/drgn -k
#
# Print the FDB *root* flow table (the HW ingress entry point) + key FDB tables
# for an mlx5 eswitch, so you can compare the ids against the HMFS dump.
#
# Usage:  drgn -k fdb_root.py [ifname]      (default ifname: p1 = 0006 uplink)
#         run for both p1 (0006, non-master) and p0 (0002, master) to compare
#
from drgn import Object
from drgn.helpers.linux import *
import sys

NETDEV_ALIGN = 32
IFNAME = sys.argv[1] if len(sys.argv) > 1 else "p1"

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

def ftinfo(label, ft):
    try:
        if not ft.value_():
            print("  %-26s: NULL" % label); return
    except Exception:
        print("  %-26s: <unavailable>" % label); return
    print("  %-26s: ft %#x  id=0x%x  level=%d  type=%s"
          % (label, ft.value_(), ft.id.value_(), ft.level.value_(), str(ft.type)))

dev = find_netdev(IFNAME)
if dev is None or not dev.value_():
    print("netdev %s not found" % IFNAME); sys.exit(1)

priv = Object(prog, 'struct mlx5e_priv', address=netdev_priv(dev))
mdev = priv.mdev
pci = mdev.pdev.dev.kobj.name.string_().decode()
print("=== netdev %s  ->  mdev %#x  (pci %s) ===" % (IFNAME, mdev.value_(), pci))

# steering mode + FDB root namespace (root_ft = the table HW enters on)
st = mdev.priv.steering
print("steering.mode:", str(st.mode))
frn = st.fdb_root_ns
if frn and frn.value_():
    print("fdb_root_ns.mode:", str(frn.mode))
    ftinfo("FDB root_ft (HW ENTRY)", frn.root_ft)
else:
    print("fdb_root_ns: NULL")

# eswitch FDB offload tables
esw = mdev.priv.eswitch
print("eswitch.mode:", str(esw.mode))
off = esw.fdb_table.offloads
ftinfo("slow_fdb", off.slow_fdb)
ftinfo("tc_miss_table", off.tc_miss_table)
# esw_chains (chain0 lives here); just show the pointer for reference
try:
    print("  esw_chains_priv           : %#x" % off.esw_chains_priv.value_())
except Exception:
    pass
