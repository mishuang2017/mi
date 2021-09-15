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

cmap = prog['sgid_map']
# print(cmap)
ids = print_cmap(cmap, "sgid_node", "id_node")

# for i, id in enumerate(ids):
#     print(id)

def print_hex_dump(buf, len):
    for j in range(len):
        if j % 16 == 0:
            if j:
                print('')
            print("%04x: " % j, end='')
        print("%02x " % (p[j]), end='')
    print('\n')

for i, id in enumerate(ids):
    len = id.sflow.action.nla_len
    attr = id.sflow.action
    print(id.refcount)
    print("id: %d, len: %d, ref: %d, hash: %x, sflow_attr: %x, userdata(cookie): %x" % \
        (id.id, len, id.refcount.count, id.hash, id.sflow.address_of_(), id.sflow.userdata))
#     print(id.sflow.ufid)
#     print(id.sflow.action)
    p = Object(prog, 'unsigned char *', address=attr.address_of_())
    if id.sflow.tunnel:
        print("tp_src: %x" % id.sflow.tunnel.tp_src)
#         print(id.sflow.tunnel)
#     print_hex_dump(p, len)

# It doesn't include the nodes whose refcount is 0
def print_metadata_map():
    cmap = prog['sgid_metadata_map']
    ids = print_cmap(cmap, "group_id_node", "metadata_node")

    for i, id in enumerate(ids):
        print("%x" % id)
        print("id: %d, inport: %d, output: %10x, refcount: %d" % \
            (id.id, id.cookie.ofp_in_port, id.cookie.sflow.output, id.refcount.count))
