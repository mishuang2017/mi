#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

sys.path.append(".")
from lib import *

# XA_MARK_PORT = XA_MARK_2 = 2, XA_MARK_MASTER = XA_MARK_1 = 1
# XA_CHUNK_SHIFT = 6 (64 slots/node), XA_MARK_LONGS = 64/64 = 1
XA_MARK_MASTER = 1
XA_MARK_PORT   = 2
XA_CHUNK_SIZE  = 64

def xa_get_mark(xa, index, mark_nr):
    """Check if xarray mark mark_nr is set for the given index.
    Works for single-level xarrays (< 64 entries).
    xa_head tagged pointer: bit1 set means internal xa_node (value - 2 = node addr).
    """
    head = xa.xa_head.value_()
    if not (head & 2):          # not an internal node — no marks
        return False
    node = Object(prog, 'struct xa_node', address=head & ~3)
    offset = index & (XA_CHUNK_SIZE - 1)
    word   = node.marks[mark_nr][offset // 64].value_()
    return bool(word & (1 << (offset % 64)))

mlx5e_priv = get_mlx5_pf0()
ldev = mlx5e_priv.mdev.priv.lag

if not ldev:
    print("No LAG device")
    sys.exit(0)

print("ldev: %#x  ports: %d  mode: %s" % (
    ldev.address_of_(), ldev.ports.value_(), ldev.mode.format_()))

entries = []
master_xa_idx = -1
for node in radix_tree_for_each(ldev.pfs.address_of_()):
    xa_idx   = node[0]
    pf       = Object(prog, 'struct lag_func', address=node[1].value_())
    pci_name = pf.dev.device.kobj.name.string_().decode()
    devfn    = pf.dev.pdev.devfn.value_()
    group_id = pf.group_id.value_()
    is_port  = xa_get_mark(ldev.pfs, xa_idx, XA_MARK_PORT)
    is_master = xa_get_mark(ldev.pfs, xa_idx, XA_MARK_MASTER)
    sd_fdb   = bool(pf.sd_fdb_active)
    if is_master:
        master_xa_idx = xa_idx
    entries.append((xa_idx, pci_name, devfn, group_id, is_port, is_master, sd_fdb))

print("master xa_idx (mlx5_lag_get_master_idx): %d" % master_xa_idx)
print("\n%-7s  %-16s  %-5s  %-10s  %-6s  %-6s  %-10s" %
      ("xa_idx", "pci_name", "devfn", "group_id", "port", "master", "sd_fdb"))
print("-" * 72)
for xa_idx, pci_name, devfn, group_id, is_port, is_master, sd_fdb in entries:
    print("%-7d  %-16s  %-5d  %-10s  %-6s  %-6s  %-10s" % (
        xa_idx,
        pci_name,
        devfn,
        ("0x%x" % group_id) if group_id else "0 (none)",
        "yes" if is_port   else "no",
        "yes" if is_master else "no",
        "yes" if sd_fdb    else "no",
    ))
