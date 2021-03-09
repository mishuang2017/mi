#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
import socket

import subprocess
import drgn
import sys
import time

sys.path.append(".")
from lib_ovs import *

backer = get_backer()
udpif = backer.udpif

print(udpif.exit_latch)
print(udpif.pause_latch)

print_seq(udpif.reval_seq, "udpif.reval_seq")
print_seq(udpif.dump_seq, "udpif.dump_seq")

# flushed_cbsets_seq = prog['flushed_cbsets_seq']
# print_seq(flushed_cbsets_seq)

# global_seqno = prog['global_seqno']
# print_seq(global_seqno)

def print_handlers():
    n1 = udpif.n_handlers
    n2 = udpif.n_revalidators

    rev = udpif.revalidators

    for i in range(n1):
    #     print("udpif.handler_id: %d" % udpif.handlers[i].handler_id)
        print(udpif.handlers[i])

    for i in range(n2):
        print(rev[i])

# dump = udpif.dump
# print(dump)
# dpif_netlink_flow_dump = Object(prog, 'struct dpif_netlink_flow_dump', address=dump.value_())
# print(dpif_netlink_flow_dump)


# ukeys = udpif.ukeys
# for i in range(512):
#     print("%d: %d" % (i, ukeys[i].cmap.impl.p.n.value_()))

n_revalidators = prog['n_revalidators']
print("n_revalidators: %d" %n_revalidators)
n_handlers = prog['n_handlers']
print("n_handlers: %d" % n_handlers)

# print_handlers()

flow_limit = udpif.flow_limit
print("flow_limit: %d" % flow_limit)

dump_duration = udpif.dump_duration
print("dump_duration: %d" % dump_duration)

reval_seq = udpif.reval_seq
# print(reval_seq)

ofproto_min_revalidate_pps = prog['ofproto_min_revalidate_pps']
print("ofproto_min_revalidate_pps: %d" % ofproto_min_revalidate_pps)

ofproto_max_revalidator = prog['ofproto_max_revalidator']
print("ofproto_max_revalidator: %d" % ofproto_max_revalidator)
