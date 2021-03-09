#!/usr/local/bin/drgn -k

# SNAT
# [root@dev-r630-03 kernel]# pedit
# reply
# mlx5e_mod_hdr_entry ffffa0bcbd53b600, mod_hdr_id 2e6
#         action_type: 1, field: 16, name: OUT_DIPV4      , offset: 0     128.0.103.87
#         action_type: 1, field:  9, name: OUT_TCP_DPORT  , offset: 0     afe8, 45032
#         action_type: 1, field:  4, name: OUT_DMAC_47_16 , offset: 0     225d013
#         action_type: 1, field:  5, name: OUT_DMAC_15_0  , offset: 0     102
#         action_type: 1, field:  1, name: OUT_SMAC_47_16 , offset: 0     248a07ad
#         action_type: 1, field:  2, name: OUT_SMAC_15_0  , offset: 0     7799
#         action_type: 1, field: 16, name: OUT_DIPV4      , offset: 0     192.168.0.2
# request
# mlx5e_mod_hdr_entry ffffa0bcb154e300, mod_hdr_id 2e5
#         action_type: 1, field: 15, name: OUT_SIPV4      , offset: 0     128.0.103.87
#         action_type: 1, field: 15, name: OUT_SIPV4      , offset: 0     8.9.10.10
#         action_type: 1, field:  8, name: OUT_TCP_SPORT  , offset: 0     ea65, 60005
#         action_type: 1, field:  4, name: OUT_DMAC_47_16 , offset: 0     248a0788
#         action_type: 1, field:  5, name: OUT_DMAC_15_0  , offset: 0     27ca
#         action_type: 1, field:  1, name: OUT_SMAC_47_16 , offset: 0     248a07ad
#         action_type: 1, field:  2, name: OUT_SMAC_15_0  , offset: 0     7799

# DNAT
# [root@dev-r630-03 kernel]# pedit
# reply
# mlx5e_mod_hdr_entry ffffa0bbc01f69c0, mod_hdr_id 2e3
#         action_type: 1, field:  4, name: OUT_DMAC_47_16 , offset: 0     248a0788
#         action_type: 1, field:  5, name: OUT_DMAC_15_0  , offset: 0     27ca
#         action_type: 1, field: 15, name: OUT_SIPV4      , offset: 0     8.9.10.10
#         action_type: 1, field:  8, name: OUT_TCP_SPORT  , offset: 0     270f, 9999
# request
# mlx5e_mod_hdr_entry ffffa0bc1199cb40, mod_hdr_id 2e2
#         action_type: 1, field:  4, name: OUT_DMAC_47_16 , offset: 0     225d013
#         action_type: 1, field:  5, name: OUT_DMAC_15_0  , offset: 0     102
#         action_type: 1, field: 16, name: OUT_DIPV4      , offset: 0     192.168.0.2
#         action_type: 1, field:  9, name: OUT_TCP_DPORT  , offset: 0     1389, 5001

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import drgn
import socket
import sys

sys.path.append("..")
from lib import *

field_name = {
    0x1: "OUT_SMAC_47_16",
    0x2: "OUT_SMAC_15_0",
    0x3: "OUT_ETHERTYPE",
    0x4: "OUT_DMAC_47_16",
    0x5: "OUT_DMAC_15_0",
    0x6: "OUT_IP_DSCP",
    0x7: "OUT_TCP_FLAGS",
    0x8: "OUT_TCP_SPORT",
    0x9: "OUT_TCP_DPORT",
    0xA: "OUT_IPV4_TTL",
    0xB: "OUT_UDP_SPORT",
    0xC: "OUT_UDP_DPORT",
    0xD: "OUT_SIPV6_127_96",
    0xE: "OUT_SIPV6_95_64",
    0xF: "OUT_SIPV6_63_32",
    0x10: "OUT_SIPV6_31_0",
    0x11: "OUT_DIPV6_127_96",
    0x12: "OUT_DIPV6_95_64",
    0x13: "OUT_DIPV6_63_32",
    0x14: "OUT_DIPV6_31_0",
    0x15: "OUT_SIPV4",
    0x16: "OUT_DIPV4",
    0x31: "IN_SMAC_47_16",
    0x32: "IN_SMAC_15_0",
    0x33: "IN_ETHERTYPE",
    0x34: "IN_DMAC_47_16",
    0x35: "IN_DMAC_15_0",
    0x36: "IN_IP_DSCP",
    0x37: "IN_TCP_FLAGS",
    0x38: "IN_TCP_SPORT",
    0x39: "IN_TCP_DPORT",
    0x3A: "IN_IPV4_TTL",
    0x3B: "IN_UDP_SPORT",
    0x3C: "IN_UDP_DPORT",
    0x3D: "IN_SIPV6_127_96",
    0x3E: "IN_SIPV6_95_64",
    0x3F: "IN_SIPV6_63_32",
    0x40: "IN_SIPV6_31_0",
    0x41: "IN_DIPV6_127_96",
    0x42: "IN_DIPV6_95_64",
    0x43: "IN_DIPV6_63_32",
    0x44: "IN_DIPV6_31_0",
    0x45: "IN_SIPV4",
    0x46: "IN_DIPV4",
    0x47: "OUT_IPV6_HOPLIMIT",
    0x48: "IN_IPV6_HOPLIMIT",
    0x49: "METADATA_REG_A",
    0x50: "METADATA_REG_B",
    0x51: "METADATA_REG_C_0",
    0x52: "METADATA_REG_C_1",
    0x53: "METADATA_REG_C_2",
    0x54: "METADATA_REG_C_3",
    0x55: "METADATA_REG_C_4",
    0x56: "METADATA_REG_C_5",
    0x57: "METADATA_REG_C_6",
    0x58: "METADATA_REG_C_7",
    0x59: "OUT_TCP_SEQ_NUM",
    0x5A: "IN_TCP_SEQ_NUM",
    0x5B: "OUT_TCP_ACK_NUM",
    0x5C: "IN_TCP_ACK_NUM"
}

def parse_pedit(l, h):
#     print("l: %lx" % l)
#     print("h: %lx" % h)
    action_type = (l & 0xf0000000) >> 28
    field = (l & 0xfff0000) >> 16
    offset = (l & 0x1f00) >> 8
    print("\taction_type: 0x%x, field: 0x%2x, name: %-15s, offset: %d" % \
        (action_type, field, field_name.get(field), offset), end="")
    if field == 0x15 or field == 0x16:
        print("\t%s" % ipv4(h))
    elif field == 0x8 or field == 0x9:
        print("\t%x, %d" % (h, h))
    else:
        print("\t%x" % (h))

def print_mod_hdr_key(key):
    actions = key.actions
    num_actions = key.num_actions
    for j in range(num_actions):
        p = Object(prog, 'void *', address=actions.value_())
        p = p.value_()
        l = socket.ntohl(p & 0xffffffff)
        h = socket.ntohl((p & 0xffffffff00000000) >> 32)
        parse_pedit(l, h)
        actions = actions + 8
