#!/usr/local/bin/drgn -k

# family:  1, create:          unix_create
# family:  2, create:          inet_create
# family: 10, create:         inet6_create
# family: 16, create:       netlink_create
# family: 17, create:        packet_create
# family: 38, create:           alg_create
# 
# type: 1, protocol:   6, prot:        tcp_prot, ops:      inet_stream_ops
# type: 1, protocol: 132, prot:       sctp_prot, ops:   inet_seqpacket_ops
# type: 2, protocol:  17, prot:        udp_prot, ops:       inet_dgram_ops
# type: 2, protocol: 136, prot:    udplite_prot, ops:       inet_dgram_ops
# type: 2, protocol:   1, prot:       ping_prot, ops:     inet_sockraw_ops
# type: 3, protocol:   0, prot:        raw_prot, ops:     inet_sockraw_ops
# type: 5, protocol: 132, prot:       sctp_prot, ops:   inet_seqpacket_ops
# 
# SOCK_STREAM: 1
# SOCK_DGRAM: 2
# SOCK_RAW: 3

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

nfs = prog['net_families']
# print(nfs)

NPROTO = 45

for i in range(NPROTO):
    nf = nfs[i]
    if nf.value_():
        print("family: %2d, create: %20s" % (nf.family.value_(), lib.address_to_name(hex(nf.create))))

inetsw = prog['inetsw']

SOCK_PACKET = prog['SOCK_PACKET']
SOCK_MAX = SOCK_PACKET.value_() + 1
print("")

for i in range(SOCK_MAX):
    head = inetsw[i]
    for a in list_for_each_entry('struct inet_protosw', head.address_of_(), 'list'):
        print("type: %d, protocol: %3d, prot: %15s, ops: %20s" % (a.type.value_(),
            a.protocol.value_(),
            lib.address_to_name(hex(a.prot)),
            lib.address_to_name(hex(a.ops))))

SOCK_STREAM = prog['SOCK_STREAM']
SOCK_DGRAM = prog['SOCK_DGRAM']
SOCK_RAW = prog['SOCK_RAW']

print("")
print("SOCK_STREAM: %d" % SOCK_STREAM.value_())
print("SOCK_DGRAM: %d" % SOCK_DGRAM.value_())
print("SOCK_RAW: %d" % SOCK_RAW.value_())
