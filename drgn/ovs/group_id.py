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

# print("================ sample_group_ids ====================")
# sample_group_ids = prog['sample_group_ids']
# print(sample_group_ids)
# ids = print_hmap(sample_group_ids.map.address_of_(), "id_node", "node")
# for i, id in enumerate(ids):
#     print(id)
 
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
#     print(id)
    len = id.sample.action.nla_len
    attr = id.sample.action
    print("id: %d, len: %d, sample: %x, userdata(cookie): %x, actions: %x, tunnel: %x" % \
        (id.id, len, id.sample.address_of_(), id.sample.userdata, id.sample.actions, id.sample.tunnel))
#     print(id.sample.ufid)
#     print(id.sample.action)
    p = Object(prog, 'unsigned char *', address=attr.address_of_())
    cookie = Object(prog, 'struct user_action_cookie', address=id.sample.userdata + 1)
#     print(cookie)
#     print(id.sample.tunnel)
    if id.sample.tunnel:
        print("tp_src: %x" % id.sample.tunnel.tp_src)
#         print(id.sample.tunnel)
#     print_hex_dump(p, len)

# It doesn't include the nodes whose refcount is 0
def print_metadata_map():
    cmap = prog['sgid_metadata_map']
    ids = print_cmap(cmap, "group_id_node", "metadata_node")

    for i, id in enumerate(ids):
        print("%x" % id)
        print("id: %d, inport: %d, output: %10x, refcount: %d" % \
            (id.id, id.cookie.ofp_in_port, id.cookie.sample.output, id.refcount.count))
