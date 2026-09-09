#!/usr/local/bin/drgn -k
#
# Compare the HCA caps that mlx5_sd_caps_supported() checks, across two (or more)
# mlx5 PFs, to find why one SD group is rejected with:
#   "Socket-Direct: can't support requested netdev combining for group id 0x..., skipping"
#
# Usage:  drgn -k sd_caps.py            # defaults to the two BDFs below
#         edit TARGETS to taste
#
from drgn import Object, cast, container_of
import drgn

# --- devices to compare (devlink kobj names == PCI BDF) ---
TARGETS = ["0002:01:00.0", "0006:01:00.0"]

# MLX5_CAP_* indices into mdev->caps.hca[]
MLX5_CAP_GENERAL   = 0
MLX5_CAP_GENERAL_2 = 0x20

# caps checked by mlx5_sd_caps_supported() that live in the GENERAL cap blocks.
# (ft_create_alias / reset_root_to_default live in NIC_TX flow-table caps and are
#  not decoded here; the raw GENERAL diff below still flags GENERAL differences.)
CAPS = [
    ("cmd_hca_cap",   MLX5_CAP_GENERAL,   "eswitch_manager"),
    ("cmd_hca_cap",   MLX5_CAP_GENERAL,   "silent_mode_set"),
    ("cmd_hca_cap",   MLX5_CAP_GENERAL,   "silent_mode_query"),
    ("cmd_hca_cap",   MLX5_CAP_GENERAL,   "cross_vhca_rqt"),
    ("cmd_hca_cap_2", MLX5_CAP_GENERAL_2, "max_rqt_vhca_id"),
]

prog = prog  # drgn global

# ---- resolve mlx5_ifc field (mlx5-bit-offset, mlx5-bit-size) from running kernel ----
# The mlx5_ifc *_bits structs store 1 byte per firmware bit, so the C byte offset
# equals the firmware bit offset and sizeof() equals the firmware bit width.
def ifc_field(typ, fld):
    t = prog.type("struct mlx5_ifc_%s_bits" % typ)
    for m in t.members:
        if m.name == fld:
            bit_off = m.bit_offset // 8            # -> firmware bit offset
            bit_sz  = drgn.sizeof(m.type)          # -> firmware bit width
            return bit_off, bit_sz
    raise LookupError(fld)

# ---- MLX5_GET() on a raw cur[] buffer (firmware data is big-endian) ----
def mlx5_get(cur_addr, bit_off, bit_sz):
    dw   = bit_off // 32
    dbit = 32 - bit_sz - (bit_off & 0x1f)
    raw  = prog.read(cur_addr + dw * 4, 4)
    val  = int.from_bytes(raw, "big")
    return (val >> dbit) & ((1 << bit_sz) - 1)

def cap_cur_addr(mdev, cap_idx):
    hca = mdev.caps.hca[cap_idx]
    if not hca.value_():
        return 0
    return hca.cur.address_of_().value_()

# ---- find mlx5_core_dev by PCI BDF via the devlink radix tree ----
def find_mdevs(targets):
    found = {}
    for node in radix_tree_for_each(prog["devlinks"].address_of_()):
        devlink = Object(prog, "struct devlink", address=node[1].value_())
        try:
            name = devlink.dev.kobj.name.string_().decode()
        except Exception:
            continue
        if name in targets and name not in found:
            mdev = Object(prog, "struct mlx5_core_dev",
                          address=devlink.priv.address_of_().value_())
            found[name] = mdev
    return found

from drgn.helpers.linux import radix_tree_for_each

mdevs = find_mdevs(TARGETS)
missing = [t for t in TARGETS if t not in mdevs]
if missing:
    print("WARNING: could not find mlx5_core_dev for: %s" % missing)

order = [t for t in TARGETS if t in mdevs]

# ---- 1) decode the named caps side by side ----
print("=" * 78)
print("mlx5_sd_caps_supported() inputs (decoded from running kernel type info)")
print("=" * 78)
hdr = "%-22s" % "cap"
for t in order:
    hdr += " | %-18s" % t
print(hdr)
print("-" * 78)
for typ, cap_idx, fld in CAPS:
    try:
        bo, bs = ifc_field(typ, fld)
    except LookupError:
        print("%-22s   (field not in this kernel's mlx5_ifc)" % fld)
        continue
    row = "%-22s" % ("%s" % fld)
    vals = []
    for t in order:
        addr = cap_cur_addr(mdevs[t], cap_idx)
        v = mlx5_get(addr, bo, bs) if addr else None
        vals.append(v)
        row += " | %-18s" % ("<no cap block>" if v is None else hex(v))
    if len(set(vals)) > 1:
        row += "   <== DIFFERS"
    print(row)

# ---- 2) raw dword diff of the GENERAL and GENERAL_2 cur[] buffers ----
for label, cap_idx in [("GENERAL", MLX5_CAP_GENERAL), ("GENERAL_2", MLX5_CAP_GENERAL_2)]:
    print()
    print("=" * 78)
    print("raw cur[] dword diff for %s (only differing dwords shown)" % label)
    print("=" * 78)
    addrs = {t: cap_cur_addr(mdevs[t], cap_idx) for t in order}
    if any(a == 0 for a in addrs.values()):
        print("  one or more devices has no %s cap block, skipping" % label)
        continue
    # length in dwords from the type of cur[]
    n = len(mdevs[order[0]].caps.hca[cap_idx].cur)
    any_diff = False
    for i in range(n):
        words = []
        for t in order:
            raw = prog.read(addrs[t] + i * 4, 4)
            words.append(int.from_bytes(raw, "big"))
        if len(set(words)) > 1:
            any_diff = True
            line = "  dw[0x%02x] (bit 0x%03x):" % (i, i * 32)
            for t, w in zip(order, words):
                line += "  %s=0x%08x" % (t, w)
            print(line)
    if not any_diff:
        print("  (identical)")

print()
print("Legend: rows marked <== DIFFERS or dwords listed above are where the two")
print("PFs disagree. Map a differing GENERAL dword back to mlx5_ifc.h cmd_hca_cap")
print("to name the exact capability that fails mlx5_sd_caps_supported().")
