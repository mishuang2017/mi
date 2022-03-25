#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append('.')
from lib import *

fib_info_hash = prog['fib_info_hash']
size = prog['fib_info_hash_size']

for i in range(size):
    for fib in hlist_for_each_entry('struct fib_info', fib_info_hash[i].address_of_(), 'fib_hash'):
        nh_common = fib.fib_nh[0].nh_common
        name = nh_common.nhc_dev.name.string_().decode()
        oif = nh_common.nhc_oif
        saddr = fib.fib_nh[0].nh_saddr
        if name == "eno1" or name == "virbr0":
            continue
        protocol = fib.fib_protocol
#         if protocol != 2:
#             continue
        print("==================================================================================================")
        print("%-15s %x" % (name, fib), end='\t')
        print("oif: %4d" % oif, end='\t');
        print("fib_protocol: %3d" % protocol, end='\t')
        print("saddr: %15s" % ipv4(ntohl(saddr.value_())), end='\t')
        print("scope: %d" % fib.fib_scope, end='\t')
        print("fib_nhs: %d" % fib.fib_nhs)
        for j in range(fib.fib_nhs):
            print_nh(fib.fib_nh[j])
        print('')

print('')
RT_SCOPE_HOST = prog['RT_SCOPE_HOST']
print("%3d: " % RT_SCOPE_HOST.value_(), end='')
print(RT_SCOPE_HOST)

RT_SCOPE_LINK = prog['RT_SCOPE_LINK']
print("%3d: " % RT_SCOPE_LINK.value_(), end='')
print(RT_SCOPE_LINK)

RT_SCOPE_UNIVERSE = prog['RT_SCOPE_UNIVERSE']
print("%3d: " % RT_SCOPE_UNIVERSE.value_(), end='')
print(RT_SCOPE_UNIVERSE)

#define RTPROT_UNSPEC           0
#define RTPROT_REDIRECT         1       /* Route installed by ICMP redirects;   */
#define RTPROT_KERNEL           2       /* Route installed by kernel            */
#define RTPROT_BOOT             3       /* Route installed during boot          */
#define RTPROT_STATIC           4       /* Route installed by administrator     */

#define RTPROT_GATED            8       /* Apparently, GateD */
#define RTPROT_RA               9       /* RDISC/ND router advertisements */
#define RTPROT_MRT              10      /* Merit MRT */
#define RTPROT_ZEBRA            11      /* Zebra */
#define RTPROT_BIRD             12      /* BIRD */
#define RTPROT_DNROUTED         13      /* DECnet routing daemon */
#define RTPROT_XORP             14      /* XORP */
#define RTPROT_NTK              15      /* Netsukuku */
#define RTPROT_DHCP             16      /* DHCP client */
#define RTPROT_MROUTED          17      /* Multicast daemon */
#define RTPROT_KEEPALIVED       18      /* Keepalived daemon */
#define RTPROT_BABEL            42      /* Babel daemon */
#define RTPROT_OPENR            99      /* Open Routing (Open/R) Routes */
#define RTPROT_BGP              186     /* BGP Routes */
#define RTPROT_ISIS             187     /* ISIS Routes */
#define RTPROT_OSPF             188     /* OSPF Routes */
#define RTPROT_RIP              189     /* RIP Routes */
#define RTPROT_EIGRP            192     /* EIGRP Routes */
