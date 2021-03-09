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

def print_ufid_tc_data(data):
    if data.ifindex:
        print("chain: %3x, prio: %d, handle: %d, ifindex: %d" %
              (data.chain, data.prio, data.handle, data.ifindex));

# print_hmap("ufid_to_tc", "ufid_tc_data")

# all_commands = prog["all_commands"]
# print(all_commands)

backer = get_backer()
udpif = backer.udpif

# sys.exit(0)

n = udpif.n_revalidators
rev = udpif.revalidators

for i in range(n):
    print("udpif.handler_id: %d" % udpif.handlers[i].handler_id)

print("udpif.n_revalidators: %d" % n)
print("revalidators: %x" % rev)


# dump = udpif.dump
# print(dump)
# dpif_netlink_flow_dump = Object(prog, 'struct dpif_netlink_flow_dump', address=dump.value_())
# print(dpif_netlink_flow_dump)

# for i in range(n):
#     print(rev[i])


# ukeys = udpif.ukeys
# for i in range(512):
#     print("%d: %d" % (i, ukeys[i].cmap.impl.p.n.value_()))


n_revalidators = prog['n_revalidators']
print("n_revalidators: %d" %n_revalidators)
n_handlers = prog['n_handlers']
print("n_handlers: %d" % n_handlers)

# struct ofproto_dpif {
#     struct ofproto up;
# }

ofproto_dpifs = print_hmap(prog['all_ofproto_dpifs_by_name'], "ofproto_dpif", "all_ofproto_dpifs_by_name_node")
for i, ofproto_dpif in enumerate(ofproto_dpifs):
    print(ofproto_dpif)
    sflow = ofproto_dpif.sflow

