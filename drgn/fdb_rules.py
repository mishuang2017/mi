#!/usr/local/bin/drgn -k
#
# Walk the eswitch FDB flow tables (root_ft + slow_fdb) and dump every rule:
# match (criteria_enable / source_port / owner_vhca / reg_c_0) -> destination(s)
# (vport num+vhca, UPLINK=wire, or next flow table).
#
# Used to find the rule that forwards uplink egress to the physical port
# (dest type UPLINK). Diff broken-vs-working (same boot) to see what is missing.
#
# NOTE: fs_core tracks the node tree for DMFS/HMFS; some fast-path rules live in
# HW (SMFS/HMFS) and may not appear here. The slow_fdb / root_ft rules do.
#
# Usage:  drgn -k fdb_rules.py [ifname]      (default: p0)
#
from drgn import Object, cast, FaultError, container_of
from drgn.helpers.linux import *
from socket import ntohl
import sys

IFNAME = sys.argv[1] if len(sys.argv) > 1 else "p0"

def const(n):
    try:    return int(prog[n].value_())
    except Exception: return None

D_VPORT  = const('MLX5_FLOW_DESTINATION_TYPE_VPORT')
D_UPLINK = const('MLX5_FLOW_DESTINATION_TYPE_UPLINK')
D_FT     = const('MLX5_FLOW_DESTINATION_TYPE_FLOW_TABLE')

def vport_label(num):
    return {0x0:"HOST_PF",0xfffe:"ECPF",0xffff:"UPLINK"}.get(num & 0xffff,"VF/SF")

def pci_of(mdev):
    try:    return mdev.pdev.dev.kobj.name.string_().decode()
    except Exception: return "?"

def fte_match(fte, mce):
    try:
        v17   = ntohl(int(fte.val[17].value_()) & 0xffffffff)  # misc: owner<<16 | source_port
        regc0 = ntohl(int(fte.val[59].value_()) & 0xffffffff)  # misc2: metadata_reg_c_0
        sport = v17 & 0xffff
        owner = (v17 >> 16) & 0xffff
        parts = ["ce=0x%x" % mce]
        if sport or owner:
            parts.append("src_port=0x%x(%s) owner=%d" % (sport, vport_label(sport), owner))
        if regc0:
            parts.append("reg_c0=0x%x" % regc0)
        if mce == 0:
            parts.append("MATCH-ALL")
        return " ".join(parts)
    except Exception as e:
        return "match?(%s)" % e

def dest_str(rule):
    try:
        d = rule.dest_attr
        t = int(d.type.value_())
        if D_UPLINK is not None and t == D_UPLINK:
            return "UPLINK(wire)"
        if D_VPORT is not None and t == D_VPORT:
            return "vport 0x%x(%s) vhca=%d" % (int(d.vport.num.value_()),
                                               vport_label(int(d.vport.num.value_())),
                                               int(d.vport.vhca_id.value_()))
        if D_FT is not None and t == D_FT:
            ft = d.ft
            return "FT %#x id=0x%x" % (ft.value_(), int(ft.id.value_())) if ft.value_() else "FT NULL"
        return "dest_type=%d" % t
    except Exception as e:
        return "dest?(%s)" % e

def walk_ft(label, ft):
    if not ft.value_():
        print("\n== %s: NULL ==" % label); return
    print("\n== %s: ft %#x id=0x%x level=%d ==" % (label, ft.value_(),
          int(ft.id.value_()), int(ft.level.value_())))
    ngrp = nfte = 0
    uplink_dests = 0
    try:
        for gnode in list_for_each_entry('struct fs_node',
                                         ft.node.children.address_of_(), 'list'):
            grp = container_of(gnode, 'struct mlx5_flow_group', 'node')
            try:    mce = int(grp.mask.match_criteria_enable.value_())
            except Exception: mce = -1
            ngrp += 1
            for fnode in list_for_each_entry('struct fs_node',
                                             grp.node.children.address_of_(), 'list'):
                fte = container_of(fnode, 'struct fs_fte', 'node')
                nfte += 1
                dests = []
                try:
                    for rnode in list_for_each_entry('struct fs_node',
                                                     fte.node.children.address_of_(), 'list'):
                        rule = container_of(rnode, 'struct mlx5_flow_rule', 'node')
                        ds = dest_str(rule)
                        dests.append(ds)
                        if "UPLINK" in ds:
                            uplink_dests += 1
                except Exception as e:
                    dests.append("<dests? %s>" % e)
                print("   fte idx=%-4d  %-46s -> %s"
                      % (int(fte.index.value_()), fte_match(fte, mce),
                         ", ".join(dests) if dests else "(no dest)"))
    except FaultError as e:
        print("   <fault walking %s: %s>" % (label, e))
    print("   [%d groups, %d ftes, %d UPLINK(wire) dests]" % (ngrp, nfte, uplink_dests))

# ---- resolve netdev -> esw ----
nd = netdev_get_by_name(prog['init_net'], IFNAME)
if not nd:
    print("netdev %s not found" % IFNAME); sys.exit(1)
priv = netdev_priv(nd, "struct mlx5e_priv")
mdev = priv.mdev
esw = mdev.priv.eswitch
if not esw.value_():
    print("%s: NULL eswitch" % IFNAME); sys.exit(1)
print("=== FDB rules on %s (pci %s, esw %#x) ===" % (IFNAME, pci_of(mdev), esw.value_()))

st = mdev.priv.steering
print("steering.mode:", str(st.mode))
frn = st.fdb_root_ns
off = esw.fdb_table.offloads

if frn and frn.value_():
    walk_ft("FDB root_ft (HW ENTRY)", frn.root_ft)
walk_ft("slow_fdb", off.slow_fdb)
walk_ft("tc_miss_table", off.tc_miss_table)
