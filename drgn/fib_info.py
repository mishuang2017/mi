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

print(size)
for i in range(size):
    for fib in hlist_for_each_entry('struct fib_info', fib_info_hash[i].address_of_(), 'fib_hash'):
        if fib.nh:
#             print(fib)
            if fib.nh.is_group:
                print("==================================================================================================")
#                 print(fib.nh.nh_grp)
                print("fib_info %x" % fib)
                for j in range(fib.nh.nh_grp.num_nh):
                    fib_nh = fib.nh.nh_grp.nh_entries[j].nh.nh_info.fib_nh
                    nh_common = fib_nh.nh_common
                    name = nh_common.nhc_dev.name.string_().decode()
                    oif = nh_common.nhc_oif
                    weight = nh_common.nhc_weight
                    print("\tnum_nh: %d, %-15s oif: %4d, weight: %d" % \
                        (j, name, oif, weight))
        else:
            print_fib_info(fib)

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

fib_info_devhash = prog['fib_info_devhash']
for i in range(1<<8):
        hlist_node = fib_info_devhash[i]
        if hlist_node.first:
                print("--------------------------------------")
#                 print(hlist_node)
                for nh in hlist_for_each_entry("struct fib_nh", hlist_node.address_of_(), "nh_hash"):
                    print_fib_nh(nh)
