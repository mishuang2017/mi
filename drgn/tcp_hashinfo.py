#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *
from socket import *

INET_LHTABLE_SIZE = 32
tcp_hashinfo = prog['tcp_hashinfo']

# TCP_ESTABLISHED = 1
# TCP_TIME_WAIT = 6

def print_sock(sock):
    global sum, sum6
#     print("%x" % sock.__sk_common.skc_rcv_saddr.value_())
    if sock.__sk_common.skc_rcv_saddr.value_() == 0x100a8c0:
        if sock.__sk_common.skc_state.value_() == 1:
            sum = sum + 1
        elif sock.__sk_common.skc_state.value_() == 6:
            sum6 = sum6 + 1

#     print("src addr: %s\t" % ipv4(ntohl(sock.__sk_common.skc_rcv_saddr.value_())), end='')
#     print("dst addr: %s\t" % ipv4(ntohl(sock.__sk_common.skc_daddr.value_())), end='')
#     print("src port: %d\t" % sock.__sk_common.skc_num.value_(), end='')
#     print("dst port: %d\t" % ntohs(sock.__sk_common.skc_dport.value_()), end='')
#     print("state %d\t" % sock.__sk_common.skc_state.value_())

ehash_mask = tcp_hashinfo.ehash_mask
print("ehash_mask: %x" % ehash_mask)
ehash = tcp_hashinfo.ehash
global sum
global sum6
sum = 0
sum6 = 0
for i in range(ehash_mask):
    head = ehash[i].chain
    if head.first.value_() & 0x1:
        continue;
    for sock in hlist_nulls_for_each_entry("struct sock", head.address_of_(), "__sk_common.skc_nulls_node"):
        print_sock(sock)
print("TCP_ESTABLISHED: %d, TCP_TIME_WAIT: %d\n" % (sum, sum6))

# print(tcp_hashinfo)

# listening_hash = tcp_hashinfo.listening_hash
# print(listening_hash)
# lhash2 = tcp_hashinfo.lhash2
# print(lhash2)

# for i in range(INET_LHTABLE_SIZE):
#     inet_listen_hashbucket  = listening_hash[i]
#     head = inet_listen_hashbucket.head
#     for sock in hlist_for_each_entry('struct sock', head.address_of_(), '__sk_common.skc_node'):
#         print(sock.__sk_common)


