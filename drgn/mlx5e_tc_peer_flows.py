#!/usr/local/bin/drgn -k

# Dumps TC peer (shared-FDB duplicate) flows, matching the struct layout
# after commit 1169c617d380 ("net/mlx5e: TC, anchor peer-flow reverse
# index on the duplicated flow") + the follow-up 7d2aff036956 ("net/mlx5e:
# TC, track peer flows in a vhca_id xarray"):
#
#   struct mlx5e_tc_flow {
#           ...
#           struct list_head peer;       /* dup: node in peer's reverse-index list */
#           ...
#           struct list_head peer_flows; /* origin: list HEAD of its dups
#                                          * dup: node on that list */
#           struct mlx5e_tc_flow *peer_orig; /* dup: back-ref to origin */
#   };
#
#   struct mlx5_eswitch {
#           ...
#           struct { ... struct xarray peer_flows; ... } offloads;
#           /* keyed by peer vhca_id -> struct list_head * (per-peer dup list) */
#   };
#
# This replaces the old flow.peer[MLX5_MAX_PORTS] / peer_used / peer_index
# fields, which no longer exist.

from drgn.helpers.linux import *
from drgn.helpers.linux.xarray import xa_for_each
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib_pedit import *

print_mlx5e_tc_flow_flags()

MLX5E_TC_FLOW_FLAG_DUP = prog['MLX5E_TC_FLOW_FLAG_DUP'].value_()

seen_esw = set()

def netdev_name(flow):
    try:
        return flow.priv.netdev.name.string_().decode()
    except Exception:
        return "?"

def print_spec_match(spec, action, indent="    "):
    """Field-decode of a tc flow's SW-side match/action, straight off
    flow->attr->parse_attr->spec (mlx5_flow_spec: match_criteria_enable +
    match_criteria[]/match_value[] in fte_match_param dword format --
    same layout print_match() in lib.py decodes for hw fs_fte, just
    read from the driver's own spec before it's programmed into hw)."""
    val = spec.match_value
    mask = spec.match_criteria

    print("%smatch_criteria_enable: %#x" % (indent, spec.match_criteria_enable.value_()))
    line = indent

    smac = (ntohl(val[0].value_()) << 16) | (ntohl(val[1].value_() & 0xffff) >> 16)
    smac_mask = (ntohl(mask[0].value_()) << 16) | (ntohl(mask[1].value_() & 0xffff) >> 16)
    if smac_mask:
        line += " smac: %012x" % smac

    dmac = (ntohl(val[2].value_()) << 16) | (ntohl(val[3].value_() & 0xffff) >> 16)
    dmac_mask = (ntohl(mask[2].value_()) << 16) | (ntohl(mask[3].value_() & 0xffff) >> 16)
    if dmac_mask:
        line += " dmac: %012x" % dmac

    ethertype = ntohl(val[1].value_() & 0xffff0000)
    if ntohl(mask[1].value_() & 0xffff0000):
        line += " et: %x" % ethertype

    ip_protocol = val[4].value_() & 0xff
    if ip_protocol:
        line += " ip_proto: %d" % ip_protocol

    ip_version = (val[4].value_() & 0x1f0000) >> 17
    if ip_version:
        line += " ipv: %x" % ip_version

    tcp_sport = ntohs(val[5].value_() & 0xffff)
    tcp_dport = ntohs(val[5].value_() >> 16 & 0xffff)
    udp_sport = ntohs(val[7].value_() & 0xffff)
    udp_dport = ntohs(val[7].value_() >> 16 & 0xffff)
    if tcp_sport or tcp_dport:
        line += " tcp sport: %d dport: %d" % (tcp_sport, tcp_dport)
    if udp_sport or udp_dport:
        line += " udp sport: %d dport: %d" % (udp_sport, udp_dport)

    src_ip = ntohl(val[11].value_())
    if src_ip:
        line += " src_ip: %s" % ipv4(src_ip)

    dst_ip = ntohl(val[15].value_())
    if dst_ip:
        line += " dst_ip: %s" % ipv4(dst_ip)

    vni = ntohl(val[21].value_() & 0xffffff) >> 8
    if vni:
        line += " vni: %d" % vni

    reg_c0 = ntohl(val[59].value_())
    if reg_c0:
        line += " reg_c0: %x" % reg_c0

    print(line)
    print("%saction: %#x" % (indent, action))

def match_action_equal(spec_a, action_a, spec_b, action_b):
    """dword-exact compare of match_criteria/match_value/action between
    two flows -- the strongest possible check that a duplicate really
    matches its origin."""
    diffs = []
    if action_a != action_b:
        diffs.append("action: %#x vs %#x" % (action_a, action_b))
    if spec_a.match_criteria_enable.value_() != spec_b.match_criteria_enable.value_():
        diffs.append("match_criteria_enable differs")
    n = len(spec_a.match_criteria)
    for i in range(n):
        if spec_a.match_criteria[i].value_() != spec_b.match_criteria[i].value_():
            diffs.append("match_criteria[%d] differs" % i)
        if spec_a.match_value[i].value_() != spec_b.match_value[i].value_():
            diffs.append("match_value[%d] differs" % i)
    return diffs

def dump_match_action(flow, label):
    spec = flow.attr.parse_attr.spec
    action = flow.attr.action.value_()
    print("  [%s] match/action for flow 0x%x on netdev %s:" % (
        label, flow.value_(), netdev_name(flow)))
    print_spec_match(spec, action)
    return spec, action

def dump_forward(flow):
    """Origin side: flow.peer_flows is the list HEAD of this flow's dups.

    ORIGIN = the real flow created by the tc filter the user actually
    added (on the netdev/vport they ran `tc filter add` on).
    PEER/DUPLICATE = the auto-installed shadow copy of that same flow,
    installed by the driver onto the peer eswitch's FDB so shared-FDB
    (LAG) steering also matches it there. Same match/cookie intent,
    different eswitch/vport.
    """
    if not (flow.flags.value_() & (1 << MLX5E_TC_FLOW_FLAG_DUP)):
        return
    print("\n########## ORIGIN flow 0x%x on netdev %s ##########" % (
        flow.value_(), netdev_name(flow)))
    print_mlx5e_tc_flow(flow)
    orig_spec, orig_action = dump_match_action(flow, "ORIGIN")

    for dup in list_for_each_entry('struct mlx5e_tc_flow',
                                   flow.peer_flows.address_of_(), 'peer_flows'):
        orig = dup.peer_orig.value_()
        match = "OK" if orig == flow.value_() else "MISMATCH!"
        print("---------- PEER/DUPLICATE flow 0x%x on netdev %s "
              "(peer_orig -> 0x%x %s) ----------" % (
            dup.value_(), netdev_name(dup), orig, match))
        print_mlx5e_tc_flow(dup)
        dup_spec, dup_action = dump_match_action(dup, "PEER")

        diffs = match_action_equal(orig_spec, orig_action, dup_spec, dup_action)
        if diffs:
            print("  !! match/action DIFFERS from origin: %s" % ", ".join(diffs))
        else:
            print("  match/action identical to origin.")

def dump_reverse_index(esw):
    """esw->offloads.peer_flows: xarray, peer_vhca_id -> struct list_head *
    of dup flows (linked via their own 'peer' member)."""
    esw_addr = esw.value_()
    if esw_addr in seen_esw:
        return
    seen_esw.add(esw_addr)

    print("\n===== esw 0x%x offloads.peer_flows (reverse index, by peer vhca_id) =====" % esw_addr)
    peer_flows_xa = esw.offloads.peer_flows
    any_entry = False
    for vhca_id, entry in xa_for_each(peer_flows_xa.address_of_()):
        any_entry = True
        list_head_addr = entry.value_()
        print("  peer vhca_id: 0x%x  list_head: 0x%x" % (vhca_id, list_head_addr))
        list_head = Object(prog, 'struct list_head', address=list_head_addr)
        count = 0
        for dup in list_for_each_entry('struct mlx5e_tc_flow',
                                       list_head.address_of_(), 'peer'):
            count += 1
            orig = dup.peer_orig
            orig_addr = orig.value_()
            print("    [%d] PEER/DUPLICATE flow: 0x%x on netdev %s  cookie: 0x%lx" % (
                count, dup.value_(), netdev_name(dup), dup.cookie.value_()))
            print("        -> ORIGIN flow: 0x%x on netdev %s (the flow the user's "
                  "tc filter actually created)" % (orig_addr, netdev_name(orig)))

            orig_spec, orig_action = dump_match_action(orig, "ORIGIN")
            dup_spec, dup_action = dump_match_action(dup, "PEER")
            diffs = match_action_equal(orig_spec, orig_action, dup_spec, dup_action)
            if diffs:
                print("        !! match/action DIFFERS from origin: %s" % ", ".join(diffs))
            else:
                print("        match/action identical to origin.")
        if count == 0:
            print("    (empty)")
    if not any_entry:
        print("  (no peers registered)")

j = 1
for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    addr = dev.value_()
    if "enp" not in name:
        continue

    mlx5e_priv = get_mlx5(dev)

    ppriv = mlx5e_priv.ppriv
    if ppriv.value_() == 0:
        continue

    print("name: %s" % name)

    mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())
    tc_ht = mlx5e_rep_priv.tc_ht

    esw = mlx5e_priv.mdev.priv.eswitch
    dump_reverse_index(esw)

    for i, flow in enumerate(hash(tc_ht, 'struct mlx5e_tc_flow', 'node')):
        j += 1
        dump_forward(flow)
