#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn.helpers.linux.xarray import xa_for_each
from drgn import Object
from socket import ntohl, ntohs
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

from lib import prog, ipv4

def offsetof(type_name, member_name):
    """Return byte offset of member in a struct/union type."""
    for m in prog.type(type_name).members:
        if m.name == member_name:
            return m.offset // 8
    raise KeyError(member_name)

def print_flow_rule(rule, indent='    '):
    dest_type = rule.dest_attr.type.value_()
    MLX5_FLOW_DESTINATION_TYPE_VPORT   = prog['MLX5_FLOW_DESTINATION_TYPE_VPORT'].value_()
    MLX5_FLOW_DESTINATION_TYPE_UPLINK  = prog['MLX5_FLOW_DESTINATION_TYPE_UPLINK'].value_()
    MLX5_FLOW_DESTINATION_TYPE_COUNTER = prog['MLX5_FLOW_DESTINATION_TYPE_COUNTER'].value_()
    MLX5_FLOW_DESTINATION_TYPE_FLOW_TABLE = prog['MLX5_FLOW_DESTINATION_TYPE_FLOW_TABLE'].value_()
    MLX5_FLOW_DESTINATION_TYPE_TIR     = prog['MLX5_FLOW_DESTINATION_TYPE_TIR'].value_()

    if dest_type == MLX5_FLOW_DESTINATION_TYPE_VPORT or \
       dest_type == MLX5_FLOW_DESTINATION_TYPE_UPLINK:
        print("%sdest: vport: 0x%x  vhca_id: 0x%x  flags: 0x%x" % (
            indent,
            rule.dest_attr.vport.num.value_(),
            rule.dest_attr.vport.vhca_id.value_(),
            rule.dest_attr.vport.flags.value_()))
        if rule.dest_attr.vport.pkt_reformat.value_():
            print("%s      reformat_id: 0x%x" % (
                indent, rule.dest_attr.vport.pkt_reformat.id.value_()))
    elif dest_type == MLX5_FLOW_DESTINATION_TYPE_COUNTER:
        print("%sdest: counter" % indent)
    elif dest_type == MLX5_FLOW_DESTINATION_TYPE_FLOW_TABLE:
        print("%sdest: ft: 0x%lx" % (indent, rule.dest_attr.ft.value_()))
    elif dest_type == MLX5_FLOW_DESTINATION_TYPE_TIR:
        print("%sdest: tir_num: 0x%x" % (indent, rule.dest_attr.tir_num.value_()))
    else:
        print("%sdest: type %d" % (indent, dest_type))

def print_fte_match(fte, indent='    '):
    try:
        if lib.fs_fte_action_exists():
            act_dests = fte.act_dests
        else:
            act_dests = fte

        val  = fte.val

        # source SQN is in outer misc (word 16), bits [31:8]
        source_sqn = ntohl(val[16].value_() & 0xffffff00)
        if source_sqn:
            print("%smatch source_sqn: 0x%x" % (indent, source_sqn))

        # source_port and source_eswitch_owner_vhca_id (word 17)
        source_port = ntohl(val[17].value_()) & 0xffff
        source_vhca = (ntohl(val[17].value_()) & 0xffff0000) >> 16
        if source_port:
            print("%smatch source_port: 0x%x" % (indent, source_port))
        if source_vhca:
            print("%smatch source_eswitch_owner_vhca_id: 0x%x" % (indent, source_vhca))

        # metadata_reg_c_0 (misc_parameters_2, word 59) -- the uplink source
        # metadata; stale (0) is the SD+MPESW forward-to-wire bug.
        reg_c0 = ntohl(val[59].value_()) & 0xffffffff
        print("%smatch metadata_reg_c_0: 0x%x%s" % (
            indent, reg_c0, "  <-- STALE/ZERO" if reg_c0 == 0 else ""))

        # metadata_reg_c_1 (word 58, one dword before reg_c_0). For the
        # send_to_vport_meta rule this carries ESW_TUN_SLOW_TABLE_GOTO_VPORT_MARK.
        reg_c1 = ntohl(val[58].value_()) & 0xffffffff
        if reg_c1:
            print("%smatch metadata_reg_c_1: 0x%x" % (indent, reg_c1))

        action = act_dests.action.action.value_()
        print("%saction flags: 0x%x" % (indent, action))

        # Destinations (children of the fte fs_node)
        for dest_node in list_for_each_entry('struct fs_node', fte.node.children.address_of_(), 'list'):
            rule_addr = dest_node.list.address_of_().value_() - \
                offsetof('struct fs_node', 'list')
            rule = Object(prog, 'struct mlx5_flow_rule', address=rule_addr)
            print_flow_rule(rule, indent + '  ')
    except Exception as e:
        print("%s<error reading fte: %s>" % (indent, e))

def print_flow_handle(handle, label, indent='  '):
    if not handle or not handle.value_():
        print("%s%s: (null)" % (indent, label))
        return
    num = handle.num_rules.value_()
    print("%s%s: mlx5_flow_handle 0x%lx  num_rules: %d" % (
        indent, label, handle.value_(), num))
    for i in range(num):
        rule_ptr = handle.rule[i]  # struct mlx5_flow_rule *
        fs_fte_node = rule_ptr.node.parent
        if fs_fte_node.value_():
            fs_fte = Object(prog, 'struct fs_fte', address=fs_fte_node.value_())
            print_fte_match(fs_fte, indent + '    ')
        else:
            print_flow_rule(rule_ptr, indent + '    ')

def dump_vport_sqs():
    # Find mlx5e rep netdevs by matching netdev_ops to mlx5e_rep_netdev_ops.
    # This guarantees we only process fully-loaded reps with valid netdevs.
    try:
        rep_ops_addr = prog['mlx5e_rep_netdev_ops'].address_of_().value_()
    except KeyError:
        rep_ops_addr = None

    print("=" * 70)
    print("vport_sqs_list for all mlx5e rep netdevs")
    print("=" * 70)

    for dev in lib.get_netdevs():
        try:
            if rep_ops_addr is not None and dev.netdev_ops.value_() != rep_ops_addr:
                continue

            netdev_name = dev.name.string_().decode('utf-8', errors='replace')
            mlx5e_priv = lib.get_mlx5(dev)

            if not mlx5e_priv.ppriv.value_():
                continue

            rpriv = Object(prog, 'struct mlx5e_rep_priv', address=mlx5e_priv.ppriv.value_())
            rep = rpriv.rep

            # check if list is empty
            list_head = rpriv.vport_sqs_list.address_of_()
            next_ptr = rpriv.vport_sqs_list.next.value_()
            list_empty = (next_ptr == list_head.value_())

            has_rx_rule = False
            try:
                has_rx_rule = bool(rpriv.vport_rx_rule.value_())
            except AttributeError:
                pass

            if list_empty and not has_rx_rule:
                continue

            print("\nnetdev: %s  vport: 0x%x  rpriv: 0x%lx" % (
                netdev_name, rep.vport.value_(), rpriv.address_of_().value_()))

            sq_idx = 0
            for rep_sq in list_for_each_entry('struct mlx5e_rep_sq',
                                              rpriv.vport_sqs_list.address_of_(), 'list'):
                rep_sq_addr = rep_sq.list.address_of_().value_() - \
                    offsetof('struct mlx5e_rep_sq', 'list')
                print("  [%d] rep_sq: 0x%lx  sqn: 0x%x" % (
                    sq_idx, rep_sq_addr, rep_sq.sqn.value_()))

                # local send-to-vport rule
                print_flow_handle(rep_sq.send_to_vport_rule, "send_to_vport_rule (local)")

                # per-peer rules in sq_peer XArray
                peer_idx = 0
                for vhca_id, entry in xa_for_each(rep_sq.sq_peer):
                    sq_peer_obj = Object(prog, 'struct mlx5e_rep_sq_peer',
                                        address=entry.value_())
                    peer_esw_ptr = sq_peer_obj.peer.value_()
                    if peer_esw_ptr:
                        print("    peer[%d] vhca_id: 0x%x  peer_esw: 0x%lx" % (
                            peer_idx, vhca_id, peer_esw_ptr))
                    else:
                        print("    peer[%d] vhca_id: 0x%x  (no peer)" % (peer_idx, vhca_id))

                    print_flow_handle(sq_peer_obj.rule, "send_to_vport_rule (peer)",
                                      indent='      ')
                    peer_idx += 1

                sq_idx += 1

            # send_to_vport_meta rule: single per rep (tunnel slow-table-goto
            # path). Matches reg_c_0 (vport metadata) + reg_c_1 (tunnel mark).
            try:
                meta = rpriv.send_to_vport_meta_rule
                if meta.value_():
                    print_flow_handle(meta, "send_to_vport_meta_rule")
                else:
                    print("  send_to_vport_meta_rule: (null)")
            except AttributeError:
                pass

            # vport_rx_rule: RX-direction rule, root FDB steers ingress
            # traffic for this vport to its rep netdev. Matches source_port
            # (or reg_c_0 in metadata mode) with no source_sqn.
            try:
                rx_rule = rpriv.vport_rx_rule
                if rx_rule.value_():
                    print_flow_handle(rx_rule, "vport_rx_rule")
                else:
                    print("  vport_rx_rule: (null)")
            except AttributeError:
                pass

        except Exception as e:
            try:
                name = dev.name.string_().decode('utf-8', errors='replace')
            except Exception:
                name = '?'
            print("\n<error on %s: %s>" % (name, e))

dump_vport_sqs()
