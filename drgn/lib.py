from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object
from drgn import cast
from socket import ntohl
from socket import ntohs
import os

import subprocess
import drgn
import socket

# print(__name__)

# prog = drgn.program_from_core_dump("/var/crash/vmcore.1")
prog = drgn.program_from_kernel()

def kernel(name):
    b = os.popen('uname -r')
    text = b.read()
    b.close()

#     print("uname -r: %s" % text)

    if name in text:
        return True
    else:
        return False

def hostname(name):
    b = os.popen('hostname -s')
    text = b.read()
    b.close()

#     print("hostname: %s" % text)

    if name in text:
        return True
    else:
        return False

pf0_name = "enp4s0f0np0"
pf1_name = "enp4s0f1np1"

pf0_name = "enp4s0f0"
pf1_name = "enp4s0f1"

(status, hostname) = subprocess.getstatusoutput("hostname")

if hostname.find("c-") == 0:
    pf0_name = "enp8s0f0"
    pf1_name = "enp8s0f1"

print("pf0_name: %s" % pf0_name)

def get_pci(name):
    (status, output) = subprocess.getstatusoutput("basename `readlink /sys/class/net/" + name + "/device`")
    return output

def name_to_address(name):
    (status, output) = subprocess.getstatusoutput("grep -w " + name + " /proc/kallsyms | awk '{print $1}'")
    print("%d, %s" % (status, output))

    if status:
        return 0

    t = int(output, 16)
    p = Object(prog, 'void *', address=t)

    return p.value_()

# hex returns type str
def address_to_name(address):
#     print(type(address))
    if address == "0x0":
        return "0x0"
#     print("address: %s" % address)
    (status, output) = subprocess.getstatusoutput("grep -a " + address.replace("0x", "") + " /proc/kallsyms | awk '{print $3}'")
#     print("%d, %s" % (status, output))

    if status:
        return ""

    return output

def ipv4(addr):
    ip = ""
    for i in range(4):
        v = (addr >> (3 - i) * 8) & 0xff
        ip += str(v)
        if i < 3:
            ip += "."
    return ip

def mac(m):
    s = ""
    for i in range(6):
        s += ("%02x" % m[i].value_())
        if i < 5:
            s += ":"
    return s

#define TCA_FLOWER_KEY_CT_FLAGS_NEW               0x01
#define TCA_FLOWER_KEY_CT_FLAGS_ESTABLISHED       0x02
#define TCA_FLOWER_KEY_CT_FLAGS_RELATED           0x04
#define TCA_FLOWER_KEY_CT_FLAGS_REPLY_DIR         0x08
#define TCA_FLOWER_KEY_CT_FLAGS_INVALID           0x10
#define TCA_FLOWER_KEY_CT_FLAGS_TRACKED           0x20
#define TCA_FLOWER_KEY_CT_FLAGS_SRC_NAT           0x40
#define TCA_FLOWER_KEY_CT_FLAGS_DST_NAT           0x80

def print_action_stats(a):
    bytes = 0
    packets = 0
    if a.cpu_bstats.value_():
        for cpu in for_each_online_cpu(prog):
            if type_exist("struct gnet_stats_basic_sync"):
                bytes += per_cpu_ptr(a.cpu_bstats, cpu).bytes.v.a.a.counter
                packets += per_cpu_ptr(a.cpu_bstats, cpu).packets.v.a.a.counter
            else:
                bstats = per_cpu_ptr(a.cpu_bstats, cpu).bstats
                bytes += bstats.bytes
                packets += bstats.packets
        print("percpu bytes: %d, packets: %d" % (bytes, packets))
    else:
        bstats = a.tcfa_bstats
        bytes += bstats.bytes.v.a.a.counter
        packets += bstats.packets.v.a.a.counter
        print("\t\t\t\tbytes: %d, packets: %d" % (bytes, packets))

    bytes = 0
    packets = 0

    if a.cpu_bstats_hw.value_():
        for cpu in for_each_online_cpu(prog):
            if type_exist("struct gnet_stats_basic_sync"):
                bytes += per_cpu_ptr(a.cpu_bstats_hw, cpu).bytes.v.a.a.counter
                packets += per_cpu_ptr(a.cpu_bstats_hw, cpu).packets.v.a.a.counter
            else:
                bstats = per_cpu_ptr(a.cpu_bstats_hw, cpu).bstats
                bytes += bstats.bytes
                packets += bstats.packets
        print("\t\t\t     hw percpu bytes: %d, packets: %d" % (bytes, packets))
    else:
#         bstats = a.tcfa_bstats_hw
#         bytes += bstats.bytes
#         packets += bstats.packets
        print("\t\t\t\thw bytes: %d, packets: %d" % (bytes, packets))
 
def print_exts(e):
    print("      nr_actions: %d" % e.nr_actions)
    for i in range(e.nr_actions):
        a = e.actions[i]
#         print(a.hw_stats)
        kind = a.ops.kind.string_().decode()
        print("        action %d: %10s: tc_action %lx" % (i+1, kind, a.value_()), end='\n')
#         print(a.cpu_bstats_hw)
#         print("hw_stats: %d" % a.hw_stats)
        if kind == "ct":
            print("\tact_ct")
#             print(a)
#             tcf_conntrack_info = Object(prog, 'struct tcf_conntrack_info', address=a.value_())
#             print("\tzone: %d" % tcf_conntrack_info.zone.value_(), end='')
#             print("\tmark: 0x%x" % tcf_conntrack_info.mark.value_(), end='')
#             print("\tlabels[0]: 0x%x" % tcf_conntrack_info.labels[0].value_(), end='')
#             print("\tcommit: %d" % tcf_conntrack_info.commit.value_(), end='')
#             print("\tnat: 0x%x" % tcf_conntrack_info.nat.value_())
#             if tcf_conntrack_info.range.min_addr.ip:
#                 print("snat ip: %s" % ipv4(ntohl(tcf_conntrack_info.range.min_addr.ip.value_())))
#             tcf_ct = cast('struct tcf_ct *', a)
#             params = tcf_ct.params
#             print("\tzone: %d\ttcf_ct_flow_table %x\tnf_flowtable %x" % (params.zone, params.ct_ft, params.nf_ft))
#             print(tcf_ct.params)

        if kind == "pedit":
            tcf_pedit = Object(prog, 'struct tcf_pedit', address=a.value_())
#             print("%lx" % a.value_())
            n = tcf_pedit.tcfp_nkeys
            print("\t\ttcf_pedit.tcfp_nkeys: %d" % n)
            for i in range(n):
                print("\t\t%d:\t" % i, end='')
                print(tcf_pedit.tcfp_keys_ex[i].htype)
                print("\t\t\toffset: %x" % tcf_pedit.tcfp_keys[i].off, end='\t')
                print("value / mask:   %08x / %08x" % (tcf_pedit.tcfp_keys[i].val, tcf_pedit.tcfp_keys[i].mask))
        if kind == "mirred":
            tcf_mirred = Object(prog, 'struct tcf_mirred', address=a.value_())
            print("\toutput: %s," % tcf_mirred.tcfm_dev.name.string_().decode(), end='\t')
            print_action_stats(a)
        if kind == "gact":
            print("\tgact action: %d (TC_ACT_SHOT = 2)" % a.tcfa_action)
            if a.goto_chain.value_():
                print("\trecirc_id: %d, 0x%x" % (a.goto_chain.index, a.goto_chain.index))
        if kind == "tunnel_key":
            tun = Object(prog, 'struct tcf_tunnel_key', address=a.value_())
            if tun.params.tcft_action == 1:
                ip_tunnel_key = tun.params.tcft_enc_metadata.u.tun_info.key
                print("\tTCA_TUNNEL_KEY_ACT_SET")
                print("\tip_tunnel_info: %x" % tun.params.tcft_enc_metadata.u.tun_info.address_of_().value_())
                print("\ttun_id: 0x%x" % ip_tunnel_key.tun_id.value_())
                print("\tsrc ip: %s" % ipv4(ntohl(ip_tunnel_key.u.ipv4.src.value_())))
                print("\tdst ip: %s" % ipv4(ntohl(ip_tunnel_key.u.ipv4.dst.value_())))
                print("\ttp_dst: %d" % ntohs(ip_tunnel_key.tp_dst.value_()))
            elif tun.params.tcft_action == 2:
                print("\tTCA_TUNNEL_KEY_ACT_RELEASE")
        if kind == "sample":
            tcf_sample = Object(prog, 'struct tcf_sample', address=a.value_())
#             print(tcf_sample)
            print("\trate: %d, truncate: %d, trunc_size: %d" % (tcf_sample.rate, tcf_sample.truncate, tcf_sample.trunc_size), end='\t')
            print("\tpsample_group_num: %d" % tcf_sample.psample_group_num)
#             print(tcf_sample.psample_group)
        if kind == "csum":
            tcf_csum = Object(prog, 'struct tcf_csum', address=a.value_())
            print("\t\tupdate_flags: %d" % tcf_csum.params.update_flags)
        if kind == "police":
            tcf_police = Object(prog, 'struct tcf_police', address=a.value_())
            print(tcf_police.params)

def print_cls_fl_filter(f):
    print("    cls_fl_filter %lx" % f.address_of_(), end=' ')
    print("handle: 0x%x" % f.handle, end=' ')
    print("in_hw_count: %d" % f.in_hw_count, end=' ')
    k = f.mkey
#     print("ct_state: 0x%x" % k.ct.ct_state)
#     print("ct_state: %x" % k.ct_state)
#     print("mask ct_state: %x" % f.mask.key.ct_state)
    #define FLOW_DIS_IS_FRAGMENT    BIT(0)
    #define FLOW_DIS_FIRST_FRAG     BIT(1)
    # 1 means nofirstfrag
    # 3 means firstfrag
#     print("ip_flags: 0x%x" % k.control.flags)
#     print("ct_state: 0x%x" % k.ct_state.value_())
#     print("ct_zone: %d" % k.ct_zone.value_())
#     print("ct_mark: 0x%x" % k.ct_mark.value_())
#     print("ct_labels[0]: %x" % k.ct_labels[0].value_())
#     print("protocol: %x" % ntohs(k.basic.n_proto))
#     print("dmac: %s" % mac(k.eth.dst))
#     print("smac: %s" % mac(k.eth.src))
#     if k.ipv4.src:
#         print("src ip: ", end='')
#         print(ipv4(ntohl(k.ipv4.src.value_())))
#     if k.ipv4.dst:
#         print("dst ip: ", end='')
#         print(ipv4(ntohl(k.ipv4.dst.value_())))
 
    print_exts(f.exts)

def get_netdevs():
    devs = []
    for net in for_each_net(prog):
        dev_base_head = net.dev_base_head.address_of_()
        for dev in list_for_each_entry('struct net_device', dev_base_head, 'dev_list'):
            devs.append(dev)
    return devs

def get_bond0():
    devs = []
    dev_base_head = prog['init_net'].dev_base_head.address_of_()
    for dev in list_for_each_entry('struct net_device', dev_base_head, 'dev_list'):
        if dev.name.string_().decode() == "bond0":
            return dev

def get_veth(veth_name):
    veths = []
    for x, dev in enumerate(get_netdevs()):
        name = dev.name.string_().decode()
        if name == veth_name:
            veth_addr = dev.value_() + prog.type('struct net_device').size
            veth = Object(prog, 'struct veth_priv', address=veth_addr)
            veths.append(veth)

            dev_peer = veth.peer
            veth_addr = dev_peer.value_() + prog.type('struct net_device').size
            veth = Object(prog, 'struct veth_priv', address=veth_addr)
            veths.append(veth)

    return veths

def get_veth_netdev(veth_name):
    devs = []
    for x, dev in enumerate(get_netdevs()):
        name = dev.name.string_().decode()
        if name == veth_name:
            veth_addr = dev.value_() + prog.type('struct net_device').size
            veth = Object(prog, 'struct veth_priv', address=veth_addr)
            devs.append(dev)

            dev_peer = veth.peer
            veth_addr = dev_peer.value_() + prog.type('struct net_device').size
            veth = Object(prog, 'struct veth_priv', address=veth_addr)
            devs.append(dev)

    return devs

def get_mlx5(dev):
    mlx5e_priv_addr = dev.value_() + prog.type('struct net_device').size
    mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)
    return mlx5e_priv

def get_mlx5e_priv(name):
    dev = netdev_get_by_name(prog['init_net'], name)
    mlx5e_priv = get_mlx5(dev)
    return mlx5e_priv

def get_mlx5_pf0():
    dev = netdev_get_by_name(prog['init_net'], pf0_name)
    mlx5e_priv = get_mlx5(dev)
    return mlx5e_priv

def get_mlx5_pf1():
    dev = netdev_get_by_name(prog['init_net'], pf1_name)
    mlx5e_priv = get_mlx5(dev)
    return mlx5e_priv

def get_pf0_netdev():
    dev = netdev_get_by_name(prog['init_net'], pf0_name)

def get_mlx5e_rep_priv():
    mlx5e_priv = get_mlx5_pf0()
    ppriv = mlx5e_priv.ppriv
    mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())

    return mlx5e_rep_priv

def get_mlx5e_rep_priv2():
    mlx5e_priv = get_mlx5_pf1()
    ppriv = mlx5e_priv.ppriv
    mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())

    return mlx5e_rep_priv

def type_exist(name):
    try:
        prog.type(name)
        return True
    except LookupError as x:
        return False

def hash(rhashtable, type, member):
    nodes = []

    tbl = rhashtable.tbl

#     print('')
#     print("rhashtable %lx" % rhashtable.address_of_())
#     print("bucket_table %lx" % tbl)
#     buckets = tbl.buckets
#     print("buckets %lx" % buckets.address_of_())

    buckets = tbl.buckets
    size = tbl.size.value_()

    print("")
    for i in range(size):
        rhash_head = buckets[i]
        if type_exist("struct rhash_lock_head"):
            rhash_head = cast("struct rhash_head *", rhash_head)
            if rhash_head.value_() == 0:
                continue
        while True:
            if rhash_head.value_() & 1:
                break
            obj = container_of(rhash_head, type, member)
            nodes.append(obj)
            rhash_head = rhash_head.next

    return nodes

# def print_mlx5_flow_handle(handle):
#     num_rules = handle.num_rules
#     for k in range(num_rules):
#         print_dest(handle.rule[k])

def print_mlx5_flow_handle(handle):
#     print("\n=== mlx5_flow_handle start ===")
    num = handle.num_rules.value_()
    print("num_rules: %d" % (num))
    for i in range(num):
        print_dest(handle.rule[i])
#     print("=== mlx5_flow_handle end ===\n")

def print_mlx5e_tc_flow_rules(rules):
#     print(rules.num_rules)
    if rules[0]:
        print_mlx5_flow_handle(rules[0])
    if rules[1]:
        print_mlx5_flow_handle(rules[1])

def print_mlx5_fc(fc):
    p = fc.lastpackets
    b = fc.lastbytes
    id = fc.id
    dummy = fc.dummy
    nr_dummies = fc.nr_dummies.counter.value_()
    cachepackets = fc.cache.packets
    cachebytes = fc.cache.bytes
    lastuse = fc.cache.lastuse
    print("mlx5_fc: %lx, id: %4x, dummy: %d, nr_dummy: %d, lastpackets: %-10ld, lastbytes: %-10ld, packets: %-10ld, bytes: %-10ld, lastuse: %-10ld" % (fc, id, dummy, nr_dummies, p, b, cachepackets, cachebytes, lastuse / 1000))
#     print(fc.cache)

def get_mlx5_core_devs():
    devs = {}

    bus_type = prog["pci_bus_type"]
    subsys_private = bus_type.p
    k_list = subsys_private.klist_devices.k_list

    for dev in list_for_each_entry('struct device_private', k_list.address_of_(), 'knode_bus.n_node'):
        addr = dev.value_()
        device_private = Object(prog, 'struct device_private', address=addr)
        device = device_private.device

        # struct pci_dev {
        #     struct device dev;
        # }
        pci_dev = container_of(device, "struct pci_dev", "dev")

        driver_data = device.driver_data
        mlx5_core = Object(prog, 'struct mlx5_core_dev', address=driver_data)
        driver = device.driver
        if driver_data.value_():
            name = driver.name.string_().decode()
            if name == "mlx5_core":
                pci_name = device.kobj.name.string_().decode()
                index = pci_name.split('.')[1]
                devs[int(index)] = mlx5_core

    return devs

def get_mlx5_core_dev(index):
    devs = get_mlx5_core_devs()
#     print(devs)
    return devs[index]

def parse_ct_status(status):
    IPS_EXPECTED = prog['IPS_EXPECTED'].value_()
    IPS_SEEN_REPLY = prog['IPS_SEEN_REPLY'].value_()
    IPS_ASSURED = prog['IPS_ASSURED'].value_()
    IPS_CONFIRMED = prog['IPS_CONFIRMED'].value_()
    IPS_SRC_NAT = prog['IPS_SRC_NAT'].value_()
    IPS_DST_NAT = prog['IPS_DST_NAT'].value_()
    IPS_SEQ_ADJUST = prog['IPS_SEQ_ADJUST'].value_()
    IPS_SRC_NAT_DONE = prog['IPS_SRC_NAT_DONE'].value_()
    IPS_DST_NAT_DONE = prog['IPS_DST_NAT_DONE'].value_()
    IPS_DYING = prog['IPS_DYING'].value_()
    IPS_FIXED_TIMEOUT = prog['IPS_FIXED_TIMEOUT'].value_()
    IPS_TEMPLATE = prog['IPS_TEMPLATE'].value_()
    IPS_UNTRACKED = prog['IPS_UNTRACKED'].value_()
    IPS_HELPER = prog['IPS_HELPER'].value_()
    IPS_OFFLOAD = prog['IPS_OFFLOAD'].value_()
    IPS_HW_OFFLOAD = prog['IPS_HW_OFFLOAD'].value_()

    print("\tstatus: %4x" % status, end=' ')
    if status & IPS_EXPECTED:
        print("IPS_EXPECTED", end=" | ")
    if status & IPS_SEEN_REPLY:
        print("IPS_SEEN_REPLY", end=" | ")
    if status & IPS_ASSURED:
        print("IPS_ASSURED", end=" | ")
    if status & IPS_CONFIRMED:
        print("IPS_CONFIRMED", end=" | ")
    if status & IPS_SRC_NAT:
        print("IPS_SRC_NAT", end=" | ")
    if status & IPS_DST_NAT:
        print("IPS_DST_NAT", end=" | ")
    if status & IPS_SEQ_ADJUST:
        print("IPS_SEQ_ADJUST", end=" | ")
    if status & IPS_SRC_NAT_DONE:
        print("IPS_SRC_NAT_DONE", end=" | ")
    if status & IPS_DST_NAT_DONE:
        print("IPS_DST_NAT_DONE", end=" | ")
    if status & IPS_DYING:
        print("IPS_DYING", end=" | ")
    if status & IPS_FIXED_TIMEOUT:
        print("IPS_FIXED_TIMEOUT", end=" | ")
    if status & IPS_TEMPLATE:
        print("IPS_TEMPLATE", end=" | ")
    if status & IPS_UNTRACKED:
        print("IPS_UNTRACKED", end=" | ")
    if status & IPS_HELPER:
        print("IPS_HELPER", end=" | ")
    if status & IPS_OFFLOAD:
        print("IPS_OFFLOAD", end=" | ")
    if status & IPS_HW_OFFLOAD:
        print("IPS_HW_OFFLOAD", end=" | ")

    print("")

# enum tcp_conntrack {
#         TCP_CONNTRACK_NONE,
#         TCP_CONNTRACK_SYN_SENT,
#         TCP_CONNTRACK_SYN_RECV,
#         TCP_CONNTRACK_ESTABLISHED,
#         TCP_CONNTRACK_FIN_WAIT,
#         TCP_CONNTRACK_CLOSE_WAIT,
#         TCP_CONNTRACK_LAST_ACK,
#         TCP_CONNTRACK_TIME_WAIT,
#         TCP_CONNTRACK_CLOSE,
#         TCP_CONNTRACK_LISTEN,   /* obsolete */
#         TCP_CONNTRACK_MAX,
#         TCP_CONNTRACK_IGNORE,
#         TCP_CONNTRACK_RETRANS,
#         TCP_CONNTRACK_UNACK,
#         TCP_CONNTRACK_TIMEOUT_MAX
# };

def get_tcp_state(state):
    TCP_CONNTRACK_ESTABLISHED = prog['TCP_CONNTRACK_ESTABLISHED'].value_()
    TCP_CONNTRACK_TIME_WAIT = prog['TCP_CONNTRACK_TIME_WAIT'].value_()
    TCP_CONNTRACK_FIN_WAIT = prog['TCP_CONNTRACK_FIN_WAIT'].value_()
    TCP_CONNTRACK_CLOSE_WAIT = prog['TCP_CONNTRACK_CLOSE_WAIT'].value_()
    TCP_CONNTRACK_CLOSE = prog['TCP_CONNTRACK_CLOSE'].value_()

    if state == TCP_CONNTRACK_ESTABLISHED:
        return "TCP_CONNTRACK_ESTABLISHED"
    elif state == TCP_CONNTRACK_TIME_WAIT:
        return "TCP_CONNTRACK_TIME_WAIT"
    elif state == TCP_CONNTRACK_FIN_WAIT:
        return "TCP_CONNTRACK_FIN_WAIT"
    elif state == TCP_CONNTRACK_CLOSE_WAIT:
        return "TCP_CONNTRACK_CLOSE_WAIT"
    elif state == TCP_CONNTRACK_CLOSE:
        return "TCP_CONNTRACK_CLOSE"

def print_tuple(tuple, ct):
    IP_CT_DIR_ORIGINAL = prog['IP_CT_DIR_ORIGINAL'].value_()
    IPPROTO_UDP = prog['IPPROTO_UDP'].value_()
    IPPROTO_TCP = prog['IPPROTO_TCP'].value_()

    protonum = tuple.tuple.dst.protonum.value_()
    dir = tuple.tuple.dst.dir.value_()
    sport = 0;
    dport = 0;
    if protonum == IPPROTO_TCP:
        dport = ntohs(tuple.tuple.dst.u.tcp.port.value_())
        sport = ntohs(tuple.tuple.src.u.tcp.port.value_())
    if protonum == IPPROTO_UDP:
        dport = ntohs(tuple.tuple.dst.u.udp.port.value_())
        sport = ntohs(tuple.tuple.src.u.udp.port.value_())
    if dport != 8080:
        return

    print("nf_conn %lx" % ct.value_())
#     print("nf_conntrack_tuple %lx" % tuple.value_())

#     if protonum == IPPROTO_TCP and dir == IP_CT_DIR_ORIGINAL:
#     if protonum == IPPROTO_UDP and dir == IP_CT_DIR_ORIGINAL:
    if protonum == IPPROTO_UDP:
        print("\tsrc ip: %20s:%6d" % (ipv4(ntohl(tuple.tuple.src.u3.ip.value_())), sport), end=' ')
        print("dst ip: %20s:%6d" % (ipv4(ntohl(tuple.tuple.dst.u3.ip.value_())), dport), end=' ')
        print("protonum: %3d" % protonum, end=' ')
        print("dir: %3d" % dir, end=' ')
        print("timeout: %3d" % ct.timeout, end=' ')
        state = ct.proto.tcp.state
        print("state: %x, tcp_state: %s" % (state, get_tcp_state(state)))
#         print("timeout: %d" % ct.timeout);
        parse_ct_status(ct.status)

def print_tun(tun):
    print("\ttun_info: id: %x, dst ip: %s, dst port: %d" % \
        (tun.key.tun_id, ipv4(ntohl(tun.key.u.ipv4.dst.value_())), \
        ntohs(tun.key.tp_dst.value_())))

def print_dest(rule):
    print("\t\tmlx5_flow_rule %lx, refcount: %d" % \
        (rule.address_of_().value_(), rule.node.refcount.refs.counter))
#     print(rule.dest_attr)
    if prog['MLX5_FLOW_DESTINATION_TYPE_COUNTER'] == rule.dest_attr.type:
        print("\t\t\tdest: counter_id: %x" % (rule.dest_attr.counter_id))
        return
    if prog['MLX5_FLOW_DESTINATION_TYPE_VPORT'] == rule.dest_attr.type or \
       prog['MLX5_FLOW_DESTINATION_TYPE_UPLINK'] == rule.dest_attr.type:
        print("\t\t\tdest: vport: %x, vhca_id: %x, flags: %x \
(MLX5_FLOW_DEST_VPORT_VHCA_ID: %x, MLX5_FLOW_DEST_VPORT_REFORMAT_ID: %x)" %
            (rule.dest_attr.vport.num, rule.dest_attr.vport.vhca_id, rule.dest_attr.vport.flags,
             prog['MLX5_FLOW_DEST_VPORT_VHCA_ID'], prog['MLX5_FLOW_DEST_VPORT_REFORMAT_ID']))
        if rule.dest_attr.vport.pkt_reformat.value_() != 0:
#             print(rule.dest_attr.vport.pkt_reformat.action.dr_action.reformat)
            print("\t\t\treformat_id: %x, %x" % (rule.dest_attr.vport.pkt_reformat.id, rule.dest_attr.vport.pkt_reformat))
        return
    if prog['MLX5_FLOW_DESTINATION_TYPE_TIR'] == rule.dest_attr.type:
        print("\t\t\tdest: tir_num: %x" % rule.dest_attr.tir_num)
        return
    if prog['MLX5_FLOW_DESTINATION_TYPE_FLOW_TABLE'] == rule.dest_attr.type:
        print("\t\t\tdest: ft: %lx" % (rule.dest_attr.ft.value_()))
#         print("----------------------------------------")
#         flow_table("goto table", rule.dest_attr.ft)
#         print("----------------------------------------")
        return
    if prog['MLX5_FLOW_DESTINATION_TYPE_FLOW_SAMPLER'] == rule.dest_attr.type:
        print("\t\t\tdest: sampler_id: %x" % rule.dest_attr.sampler_id)
        return
    if prog['MLX5_FLOW_DESTINATION_TYPE_NONE'] == rule.dest_attr.type:
        print("\t\t\tMLX5_FLOW_DESTINATION_TYPE_NONE")
    else:
        print(rule.dest_attr.type)
        print(rule)


def print_mlx5_esw_flow_attr(attr):
    print("\t\taction: %x" % attr.action, end='\t')
    print("chain: %x" % attr.chain, end='\t')
    print("dest_chain: %x" % attr.dest_chain, end='\t')
    print("prio: %x" % attr.prio, end='\t')
    print("ft: %20x" % attr.ft, end='\t')
    print("dest_ft: %20x" % attr.dest_ft, end='\t')
#     print(attr.modify_hdr)
    print('')

def flow_table2(name, table):
    print("\nflow table name: %s\nflow table id: %x leve: %x, type: %x (FS_FT_FDB: %d, FS_FT_NIC_RX: %d)" % \
        (name, table.id.value_(), table.level.value_(), table.type, prog['FS_FT_FDB'], prog['FS_FT_NIC_RX']))
    print("mlx5_flow_table %lx" % table.address_of_())
#     print("flow table address")
#     print("%lx" % table.value_())
    fs_node = Object(prog, 'struct fs_node', address=table.address_of_())
#     print("%lx" % fs_node.address_of_())
#     print(fs_node)
    group_addr = fs_node.address_of_()
#     print("fs_node address")
#     print("%lx" % group_addr.value_())
    group_addr = fs_node.children.address_of_()
#     print(group_addr)
    for group in list_for_each_entry('struct fs_node', group_addr, 'list'):
        print("mlx5_flow_group %lx" % group)
        fte_addr = group.children.address_of_()
        for fte in list_for_each_entry('struct fs_node', fte_addr, 'list'):
            fs_fte = Object(prog, 'struct fs_fte', address=fte.value_())
            print_match(fs_fte)
            dest_addr = fte.children.address_of_()
            for dest in list_for_each_entry('struct fs_node', dest_addr, 'list'):
                rule = Object(prog, 'struct mlx5_flow_rule', address=dest.value_())
                print_dest(rule)

def print_mlx5_flow_group_dr(group):
    mlx5_fs_dr_matcher =  group.fs_dr_matcher
    print("========================== mlx5_fs_dr_matcher ========================")
    print(mlx5_fs_dr_matcher.dr_matcher)

def flow_table(name, table):
    print("\nflow table name: %s\nflow table id: %x table_level: %x, \
        type: %x (FS_FT_FDB: %d, FS_FT_NIC_RX: %d, max_fte: %d, %x), refcount: %d" % \
        (name, table.id.value_(), table.level.value_(), table.type, \
        prog['FS_FT_FDB'], prog['FS_FT_NIC_RX'], table.max_fte, table.max_fte, \
        table.node.refcount.refs.counter))
    print("mlx5_flow_table %lx" % table.value_())
#     print("flow table address")
#     print("%lx" % table.value_())
    fs_node = Object(prog, 'struct fs_node', address=table.value_())
#     print("%lx" % fs_node.address_of_())
#     print(fs_node)
    group_addr = fs_node.address_of_()
#     print("fs_node address")
#     print("%lx" % group_addr.value_())
    group_addr = fs_node.children.address_of_()
#     print(group_addr)
    for group in list_for_each_entry('struct fs_node', group_addr, 'list'):
        mlx5_flow_group = Object(prog, 'struct mlx5_flow_group', address=group.value_())
#         print(mlx5_flow_group)
#         print_mlx5_flow_group_dr(mlx5_flow_group)
        match_criteria_enable = mlx5_flow_group.mask.match_criteria_enable
        mask = mlx5_flow_group.mask.match_criteria
        print("mlx5_flow_group %lx, id: %d, match_criteria_enable: %#x, refcount: %d, max_ftes: %d" % \
            (group, mlx5_flow_group.id, match_criteria_enable, \
             mlx5_flow_group.node.refcount.refs.counter, mlx5_flow_group.max_ftes))
        fte_addr = group.children.address_of_()
        for fte in list_for_each_entry('struct fs_node', fte_addr, 'list'):
            fs_fte = Object(prog, 'struct fs_fte', address=fte.value_())
            print_match(fs_fte, mask)
            if fs_fte.action.action & 0x40:
                print("modify_hdr id: %x" % fs_fte.action.modify_hdr.id)
            dest_addr = fte.children.address_of_()
            for dest in list_for_each_entry('struct fs_node', dest_addr, 'list'):
                rule = Object(prog, 'struct mlx5_flow_rule', address=dest.value_())
                print_dest(rule)

def print_mac(mac):
    for i in range(6):
        v = (mac >> (5 - i) * 8) & 0xff
        print("%02x" % v, end='')
        if i < 5:
            print(":", end='')

def print_fs_dr_rule(fte):
    print(fte.fs_dr_rule)
    dr_rule = fte.fs_dr_rule.dr_rule
    print(dr_rule)
    print(dr_rule.matcher)
#     print(dr_rule.tx.nic_matcher.s_htbl.ste_arr)
#     print(dr_rule.rx.nic_matcher.s_htbl.ste_arr)

#     rule_actions_list = fte.fs_dr_rule.dr_rule.rule_actions_list
#     print(rule_actions_list)
#     for mlx5dr_rule_action_member in list_for_each_entry('struct mlx5dr_rule_action_member', rule_actions_list.address_of_(), 'list'):
#         print(mlx5dr_rule_action_member.action)

#     print(fte.fs_dr_rule.dr_actions[0])
#     print(fte.fs_dr_rule.dr_actions[1])

def print_match(fte, mask):
#     print_fs_dr_rule(fte)
    print("fs_fte %lx\tflow_source: %x (0: any, 1: uplink: 2: local), refcount: %d" % \
        (fte.address_of_().value_(), fte.flow_context.flow_source, fte.node.refcount.refs.counter))
    val = fte.val
#     print(val)
#     smac = str(ntohl(hex(val[0])))
    print("%8x: " % fte.index.value_(), end='')
    tag = fte.flow_context.flow_tag
    if tag:
        print(" flow_tag: %x" % tag, end=' ')
    smac_47_16 = ntohl(val[0].value_())
    smac_15_0 = ntohl(val[1].value_() & 0xffff)
    smac_47_16 <<= 16
    smac_15_0 >>= 16
    smac = smac_47_16 | smac_15_0

    smac_47_16_mask = ntohl(mask[0].value_())
    smac_15_0_mask = ntohl(mask[1].value_() & 0xffff)
    smac_47_16_mask <<= 16
    smac_15_0_mask >>= 16
    smac_mask = smac_47_16_mask | smac_15_0_mask

    if smac_mask:
        print(" s: ", end='')
        print_mac(smac)

    dmac_47_16 = ntohl(val[2].value_())
    dmac_15_0 = ntohl(val[3].value_() & 0xffff)
    dmac_47_16 <<= 16
    dmac_15_0 >>= 16
    dmac = dmac_47_16 | dmac_15_0

    dmac_47_16_mask = ntohl(mask[2].value_())
    dmac_15_0_mask = ntohl(mask[3].value_() & 0xffff)
    dmac_47_16_mask <<= 16
    dmac_15_0_mask >>= 16
    dmac_mask = dmac_47_16_mask | dmac_15_0_mask

    if dmac_mask:
        print(" d: ", end='')
        print_mac(dmac)

    ethertype_mask = ntohl(mask[1].value_() & 0xffff0000)
    ethertype = ntohl(val[1].value_() & 0xffff0000)
    if ethertype_mask:
        print(" et: %x" % ethertype, end='')

#     vport = ntohl(val[17].value_() & 0xffff0000)
#     metadata_reg_c_0
    vport = ntohl(val[59].value_() & 0xffff0000)
    if vport:
        print(" vport: %4x" % vport, end='')

    ip_protocol = val[4].value_() & 0xff
    if ip_protocol:
        print(" ip: %-2d" % ip_protocol, end='')

    tos = (val[4].value_() & 0xff00) >> 8
    if tos:
        print(" tos: %-2x(dscp: %x)" % (tos, tos >> 2), end='')

    tcp_flags = (val[4].value_() & 0xff000000) >> 24
    if tcp_flags:
        print(" tflags: %2x" % tcp_flags, end='')

    ip_version = (val[4].value_() & 0x1f0000) >> 17
    if ip_version:
        print(" ipv: %-2x" % ip_version, end='')

    cvlan = (val[4].value_() & 0xe00000) >> 23
    if cvlan:
        print(" cvlan: %-2x" % cvlan, end='')

    tcp_sport = ntohs(val[5].value_() & 0xffff)
    if tcp_sport:
        print(" sport: %5d" % tcp_sport, end='')

    tcp_dport = ntohs(val[5].value_() >> 16 & 0xffff)
    if tcp_dport:
        print(" dport: %6d" % tcp_dport, end='')

    udp_sport = ntohs(val[7].value_() & 0xffff)
    if udp_sport:
        print(" sport: %6d" % udp_sport, end='')

    udp_dport = ntohs(val[7].value_() >> 16 & 0xffff)
    if udp_dport:
        print(" dport: %6d" % udp_dport, end='')

    src_ip = ntohl(val[11].value_())
    if src_ip:
        print(" src_ip: %12s" % ipv4(src_ip), end='')

    dst_ip = ntohl(val[15].value_())
    if dst_ip:
        print(" dst_ip: %12s" % ipv4(dst_ip), end='')

    vni = ntohl(val[21].value_() & 0xffffff) >> 8
    if vni:
        print(" vni: %6d" % vni, end='')

    source_sqn = ntohl(val[16].value_() & 0xffffff00)
    if source_sqn:
        print(" source_sqn: %6x" % source_sqn, end='')

    source_eswitch_owner_vhca_id = (ntohl(val[17].value_()) & 0xffff0000) >> 16
    source_eswitch_owner_vhca_id_mask = (ntohl(mask[17].value_()) & 0xffff0000) >> 16
    if source_eswitch_owner_vhca_id_mask:
        print(" source_eswitch_owner_vhca_id: %6x" % source_eswitch_owner_vhca_id, end='')

    source_port = ntohl(val[17].value_()) & 0xffff
    source_port_mask = ntohl(mask[17].value_()) & 0xffff
    if source_port_mask:
        print(" source_port: %6x" % source_port, end='')

    reg_c5 = ntohl(val[54].value_())
    reg_c5_mask = ntohl(mask[54].value_())
    if reg_c5_mask:
        print(" reg_c5 (fteid, meter red: 0, green: 2): %4x" % reg_c5, end='')

    reg_c2 = ntohl(val[57].value_())
    if reg_c2:
        print(" reg_c2 (ct_state|ct_zone, est=2, trk=4, nat=8): %4x" % reg_c2, end='')

    reg_c1 = ntohl(val[58].value_())
    if reg_c1:
        print(" reg_c1: %4x" % reg_c1, end='')

    reg_c0 = ntohl(val[59].value_())
    if reg_c0:
        print(" reg_c0: %4x" % reg_c0, end='')

    if vni:
        smac_47_16 = ntohl(val[32].value_())
        smac_15_0 = ntohl(val[33].value_() & 0xffff)
        smac_47_16 <<= 16
        smac_15_0 >>= 16
        smac = smac_47_16 | smac_15_0
        print("\n           s: ", end='')
        print_mac(smac)

        dmac_47_16 = ntohl(val[34].value_())
        dmac_15_0 = ntohl(val[35].value_() & 0xffff)
        dmac_47_16 <<= 16
        dmac_15_0 >>= 16
        dmac = dmac_47_16 | dmac_15_0
        print(" d: ", end='')
        print_mac(dmac)

        ethertype_mask = ntohl(mask[33].value_() & 0xffff0000)
        ethertype = ntohl(val[33].value_() & 0xffff0000)
        if ethertype_mask:
            print(" et: %x" % ethertype, end='')

        ip_protocol = val[36].value_() & 0xff
        if ip_protocol:
            print(" ip: %-2d" % ip_protocol, end='')

        tos = (val[4].value_() & 0xff00) >> 8
        if tos:
            print(" tos: %-2x(dscp: %x)" % (tos, tos >> 2), end='')

        tcp_flags = (val[36].value_() & 0xff000000) >> 24
        if tcp_flags:
            print(" tflags: %2x" % tcp_flags, end='')

        ip_version = (val[36].value_() & 0xff0000) >> 17
        if ip_version:
            print(" ipv: %-2x" % ip_version, end='')

        tcp_sport = ntohs(val[37].value_() & 0xffff)
        if tcp_sport:
            print(" sport: %5d" % tcp_sport, end='')

        tcp_dport = ntohs(val[37].value_() >> 16 & 0xffff)
        if tcp_dport:
            print(" dport: %6d" % tcp_dport, end='')

        udp_sport = ntohs(val[39].value_() & 0xffff)
        if udp_sport:
            print(" sport: %6d" % udp_sport, end='')

        udp_dport = ntohs(val[39].value_() >> 16 & 0xffff)
        if udp_dport:
            print(" dport: %6d" % udp_dport, end='')

        src_ip = ntohl(val[43].value_())
        if src_ip:
            print(" src_ip: %12s" % ipv4(src_ip), end='')

        dst_ip = ntohl(val[47].value_())
        if src_ip:
            print(" dst_ip: %12s" % ipv4(dst_ip), end='')

    print(" action: %4x" % fte.action.action.value_())


### CT ###

def print_flow_offload_tuple(t):
#     print(t)
    print("\t\tflow_offload_tuple %lx" % t.address_of_())
    print("\t\tsrc_v4: %10s" % ipv4(socket.ntohl(t.src_v4.s_addr.value_())), end='\t')
    print("dst_v4: %10s" % ipv4(socket.ntohl(t.dst_v4.s_addr.value_())), end='\t')
    print("src_port: %6d" % socket.ntohs(t.src_port.value_()), end='\t')
    print("dst_port: %6d" % socket.ntohs(t.dst_port.value_()), end='\t')
    print("l3proto: %2d" % t.l3proto.value_(), end='\t')
    print("l4proto: %2d" % t.l4proto.value_(), end='\t')
    print("dir: %d" % t.dir.value_(), end='\t')
    print('')

def print_flow_offload(flow, dir):
    print("\tflow_offload %lx" % flow)
    if dir == 0:
        print("\tdir = 0")
    else:
        print("\tdir = 1")
    print("\t\tnf_conn %lx" % flow.ct)
    print("\t\tflags: %x, timeout: %x, type: %d" % (flow.flags, flow.timeout, flow.type), end='\t')
    print("(NF_FLOW_SNAT: %x)" % (1 << prog['NF_FLOW_SNAT'].value_()), end=' ')
    print("(NF_FLOW_HW: %x)" % (1 << prog['NF_FLOW_HW'].value_()))
#     print(flow)

def print_tuple_rhash_tuple(tuple_rhash):
        tuple = tuple_rhash.tuple
        dir = tuple.dir.value_()
        if dir == 0:
            flow_offload = cast("struct flow_offload *", tuple_rhash)
            print_flow_offload(flow_offload, dir)
        else:
            flow_offload = Object(prog, 'struct flow_offload', address=tuple_rhash.value_() - \
                prog.type('struct flow_offload_tuple_rhash').size)
            print_flow_offload(flow_offload.address_of_(), dir)
        print_flow_offload_tuple(tuple)

def get_pcpu_refcnt(dev):
    count = 0
    for cpu in for_each_online_cpu(prog):
#         print(cpu, end='\t')
        pointer = per_cpu_ptr(dev.pcpu_refcnt, cpu)
        refcnt = Object(prog, 'int', address=pointer)
#         print("%8d" % refcnt, end='\t')
#         print(pointer)
        count += refcnt
    return count

def print_vxlan_udphdr(x):
    print("\n=== vxlan udp header start ===")
    print("dest mac          : %02x:%02x:%02x:%02x:%02x:%02x" % (x[0], x[1], x[2], x[3], x[4], x[5]))
    print("src mac           : %02x:%02x:%02x:%02x:%02x:%02x" % (x[6], x[7], x[8], x[9], x[10], x[11]))
    print("ethertype         : 0x%02x%02x" % (x[12], x[13]))
    print("version|IHL       : 0x%02x" % (x[14]))
    print("DSCP|ECN          : 0x%02x" % (x[15]))
    print("total length      : 0x%02x%02x" % (x[16], x[17]))
    print("identification    : 0x%02x%02x" % (x[18], x[19]))
    print("flags|frag offset : 0x%02x%02x" % (x[20], x[21]))
    print("tme to live       : 0x%02x" % (x[22]))
    print("protocol          : 0x%02x" % (x[23]))
    print("header checksum   : 0x%02x%02x" % (x[24], x[25]))
    print("source IP address : %d.%d.%d.%d" % (x[26], x[27], x[28], x[29]))
    print("  dest IP address : %d.%d.%d.%d" % (x[30], x[31], x[32], x[33]))
    print("UDP source port   : %d" % (x[34] << 8 | x[35]))
    print("UDP dest port     : %d" % (x[36] << 8 | x[37]))
    print("UDP length        : %d" % (x[38] << 8 | x[39]))
    print("UDP checksum      : %02x%02x" % (x[40], x[41]))
    print("vxlan(VNI present): %02x%02x%02x%02x" % (x[42], x[43], x[44], x[45]))
    print("vxlan(VNI)        : %d" % (x[46] << 16 | x[47] << 8 | x[48]))
    print("vxlan(reserved)   : %d" % (x[49]))
    print("=== vxlan udp header end ===\n")

def print_mlx5e_encap_entry(e):
    print("--- mlx5e_encap_entry ---")
#     print(e)
#     print("remote_ifindex: %d" % e.remote_ifindex)
    print("out_dev: %s" % e.out_dev.name.string_().decode())
    print("route_dev_ifindex: %s" % e.route_dev_ifindex)
#     print(e.encap_header)
    x = Object(prog, 'unsigned char *', address=e.encap_header.address_of_())
    print_vxlan_udphdr(x)
    print("encap_size: %d" % e.encap_size)
#     for i in range(e.encap_size):
#         print("%#x " % e.encap_header[i])
    print("mlx5e_encap_entry %lx" % e.value_())
    print_tun(e.tun_info)
    print(e.pkt_reformat)
    print("--- end ---")

def print_mlx5e_tc_flow_flags():
    print("MLX5_MATCH_OUTER_HEADERS          %10x" % prog['MLX5_MATCH_OUTER_HEADERS'].value_())
    print("MLX5_MATCH_MISC_PARAMETERS        %10x" % prog['MLX5_MATCH_MISC_PARAMETERS'].value_())
    print("MLX5_MATCH_MISC_PARAMETERS_2      %10x" % prog['MLX5_MATCH_MISC_PARAMETERS_2'].value_())
    print('')
    print("MLX5E_TC_FLOW_FLAG_INGRESS        %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_INGRESS'].value_()))
    print("MLX5E_TC_FLOW_FLAG_EGRESS         %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_EGRESS'].value_()))
    print("MLX5E_TC_FLOW_FLAG_NIC            %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_NIC'].value_()))
    print("MLX5E_TC_FLOW_FLAG_ESWITCH        %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_ESWITCH'].value_()))
    print('')
    print("MLX5E_TC_FLOW_FLAG_FT             %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_FT'].value_()))
    print("MLX5E_TC_FLOW_FLAG_OFFLOADED      %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_OFFLOADED'].value_()))
    print("MLX5E_TC_FLOW_FLAG_HAIRPIN        %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_HAIRPIN'].value_()))
    print("MLX5E_TC_FLOW_FLAG_HAIRPIN_RSS    %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_HAIRPIN_RSS'].value_()))
    print('')
    print("MLX5E_TC_FLOW_FLAG_SLOW           %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_SLOW'].value_()))
    print("MLX5E_TC_FLOW_FLAG_DUP            %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_DUP'].value_()))
    print("MLX5E_TC_FLOW_FLAG_NOT_READY      %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_NOT_READY'].value_()))
    print("MLX5E_TC_FLOW_FLAG_DELETED        %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_DELETED'].value_()))
    print('')
    print("MLX5E_TC_FLOW_FLAG_CT             %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_CT'].value_()))
    print("MLX5E_TC_FLOW_FLAG_L3_TO_L2_DECAP %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_L3_TO_L2_DECAP'].value_()))
    print("MLX5E_TC_FLOW_FLAG_TUN_RX         %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_TUN_RX'].value_()))
    print("MLX5E_TC_FLOW_FLAG_FAILED         %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_FAILED'].value_()))
    print('')
    print("MLX5E_TC_FLOW_FLAG_SAMPLE         %10x" % (1 << prog['MLX5E_TC_FLOW_FLAG_SAMPLE'].value_()))

def print_mlx5e_tc_flow_parse_attr(parse_attr):
    print("--- mlx5e_tc_flow_parse_attr---")
    print("parse_attr.mirred_ifindex[0]: %d" % parse_attr.mirred_ifindex[0])
    print("parse_attr.mirred_ifindex[1]: %d" % parse_attr.mirred_ifindex[1])
    tun_info = parse_attr.tun_info[0]
    if tun_info.value_():
        print("parse_attr.tun_info[0]")
        print_tun(tun_info)

    filter_dev = parse_attr.filter_dev
    print("filter_dev name: %s" % filter_dev.name.string_().decode())
    print("---end---")

def print_mlx5_rx_tun_attr(tun_attr):
    print(tun_attr)
#     print("\tmlx5_rx_tun_attr: src_ip: %s, dst_ip: %s" % \
#         (ipv4(ntohl(tun_attr.src_ip.v4)), ipv4(ntohl(tun_attr.dst_ip.v4))))

def print_mlx5e_tc_flow(flow):
    print("mlx5e_tc_flow           %x" % flow)
    print("mlx5e_tc_flow.peer_flow %x" % flow.peer_flow)
    MLX5_ESW_DEST_ENCAP = prog['MLX5_ESW_DEST_ENCAP']
    MLX5_ESW_DEST_ENCAP_VALID = prog['MLX5_ESW_DEST_ENCAP_VALID']
    MLX5_ESW_DEST_CHAIN_WITH_SRC_PORT_CHANGE = prog['MLX5_ESW_DEST_CHAIN_WITH_SRC_PORT_CHANGE']

    print("===============================")
    name = flow.priv.netdev.name.string_().decode()
#     print(flow.decap_route)
    print_mlx5e_tc_flow_rules(flow.rule)
    flow_attr = flow.attr
#     print(flow_attr)
    esw_attr = flow_attr.esw_attr[0]
#     if not esw_attr.dests[0].flags & MLX5_ESW_DEST_ENCAP_VALID:
#         print("not encap, return")
#         return
    parse_attr = flow_attr.parse_attr
#     print("%-14s mlx5e_tc_flow %lx, cookie: %lx, flags: %x, refcnt: %d" % \
#         (name, flow.value_(), flow.cookie.value_(), flow.flags.value_(), flow.refcnt.refs.counter))
    print("chain: %x, prio: %d" % (flow_attr.chain, flow_attr.prio), end='\t')
    print("dest_chain: %x" % flow_attr.dest_chain, end='\t')
    print("ft: %x" % flow_attr.ft, end='\t')
    print("dest_ft: %x" % flow_attr.dest_ft, end='\t')
    print("ct_state: %x/%x" % (parse_attr.spec.match_value[57] >> 8, parse_attr.spec.match_criteria[57] >> 8))
    print("mlx5_flow_spec %lx" % parse_attr.spec.address_of_())

    MLX5_FLOW_CONTEXT_ACTION_DECAP = prog['MLX5_FLOW_CONTEXT_ACTION_DECAP']
    MLX5_FLOW_CONTEXT_ACTION_PACKET_REFORMAT = prog['MLX5_FLOW_CONTEXT_ACTION_PACKET_REFORMAT']
    print("action: %x" % flow_attr.action, end='\t')
    if flow_attr.action & MLX5_FLOW_CONTEXT_ACTION_PACKET_REFORMAT:
        print("MLX5_FLOW_CONTEXT_ACTION_PACKET_REFORMAT")
    elif flow_attr.action & MLX5_FLOW_CONTEXT_ACTION_DECAP:
        print("MLX5_FLOW_CONTEXT_ACTION_DECAP")
    else:
        print("")

#     print(flow_attr.sample_attr)

#     print(esw_attr)
    if esw_attr.dests[0].flags & MLX5_ESW_DEST_ENCAP:
        print(MLX5_ESW_DEST_ENCAP)
    if esw_attr.dests[0].flags & MLX5_ESW_DEST_ENCAP_VALID:
        print(MLX5_ESW_DEST_ENCAP_VALID)
        if esw_attr.dests[0].termtbl:
#             print("reformat id: %x, termtbl.flow_act.pkt_reformat %x" %
#                 (esw_attr.dests[0].termtbl.flow_act.pkt_reformat.action.dr_action.reformat.id,
#                 esw_attr.dests[0].termtbl.flow_act.pkt_reformat))
            print("flow.encaps[0].e: %x" % flow.encaps[0].e)
    if esw_attr.dests[0].flags & MLX5_ESW_DEST_CHAIN_WITH_SRC_PORT_CHANGE:
        print(MLX5_ESW_DEST_CHAIN_WITH_SRC_PORT_CHANGE)

    print_mlx5_rx_tun_attr(esw_attr.rx_tun_attr)

#     if flow.flags.value_() & 1 << prog['MLX5E_TC_FLOW_FLAG_SAMPLE']:
#         print(esw_attr)
#         print("mlx5_esw_flow_attr %lx" % esw_attr.address_of_())
#         print(parse_attr.mod_hdr_acts)
#     print("match_criteria_enable: %x" % flow.esw_attr[0].parse_attr.spec.match_criteria_enable)
#     print(flow.esw_attr[0].parse_attr)
#     print(flow_attr.modify_hdr)
#     print(flow_attr.parse_attr)
#     print(flow_attr.parse_attr.mod_hdr_acts)
#     print("tunnel_id: %x" % flow.tunnel_id)

    print_mlx5e_tc_flow_parse_attr(parse_attr)
    print("")

    return
#     print(flow.miniflow_list)

    j = 0
    for mlx5e_miniflow_node in list_for_each_entry('struct mlx5e_miniflow_node', flow.miniflow_list.address_of_(), 'node'):
#         print(mlx5e_miniflow_node)
        print("\t%d: mlx5e_miniflow %lx" % (j, mlx5e_miniflow_node.miniflow.value_()))
        j = j + 1

def get_fib_type(type):
    if type == 1:
        return "RTN_UNICAST"
    elif type == 2:
        return "RTN_LOCAL"
    elif type == 3:
        return "RTN_BROADCAST"
    else:
        return "others"

def print_fib_nh(nh):
    fib_info = nh.nh_parent
    name = nh.nh_common.nhc_dev.name.string_().decode()
    fib_type = nh.nh_parent.fib_type.value_()
    fib_scope = nh.nh_common.nhc_scope.value_()

#     if fib_scope == prog['RT_SCOPE_NOWHERE'].value_():
#         return
#     if fib_type == broadcast.value_():
#         return
#     if name != "br" and name != "enp4s0f0":
#         return

#     print("fib_nh %lx" % nh)
    print("\tname: %10s" % name, end='')
    print("  saddr: %15s" % ipv4(socket.ntohl(nh.nh_saddr.value_())), end='')
    print("  gw: %15s" % ipv4(socket.ntohl(nh.nh_common.nhc_gw.ipv4.value_())), end='')
    print("  weight: %4d" % nh.nh_common.nhc_weight.value_(), end='')
    print("  scope: %4d" % nh.nh_common.nhc_scope.value_(), end='')
    print("  flags: %4x" % nh.nh_common.nhc_flags.value_(), end='')
#     print("  fib_info: %lx" % nh.nh_parent.value_(), end='')
    print("  fib_type: %s" % get_fib_type(nh.nh_parent.fib_type), end='')
    print('')
#     print_info(fib_info)

def print_fib_info(fib):
    nh_common = fib.fib_nh[0].nh_common
    name = nh_common.nhc_dev.name.string_().decode()
    oif = nh_common.nhc_oif
    saddr = fib.fib_nh[0].nh_saddr
    if name != pf0_name and name != pf1_name:
        return
    protocol = fib.fib_protocol
#     if protocol != 2:
#         return
    print("==================================================================================================")
    print("%-15s %x" % (name, fib), end='\t')
    print("oif: %4d" % oif, end='\t');
    print("fib_protocol: %3d" % protocol, end='\t')
    print("saddr: %15s" % ipv4(ntohl(saddr.value_())), end='\t')
    print("scope: %d" % fib.fib_scope, end='\t')
    print("fib_nhs: %d" % fib.fib_nhs)
    for j in range(fib.fib_nhs):
        print_fib_nh(fib.fib_nh[j])

def print_completion(completion):
    task_list = completion.wait.task_list
    for swait_queue in list_for_each_entry('struct swait_queue', task_list.address_of_(), 'task_list'):
#         print(swait_queue)
        trace = prog.stack_trace(swait_queue.task)
        print(trace)
