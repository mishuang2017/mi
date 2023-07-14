#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

dev_index_head = prog['init_net'].dev_index_head

for i in range(128):
    for dev in hlist_for_each_entry('struct net_device', dev_index_head, 'index_hlist'):
        name = dev.name.string_().decode()
        print("name: %-20s, index: %d" % (name, dev.ifindex))
    dev_index_head = dev_index_head + 1
