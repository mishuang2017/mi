#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object

dev_name_head = prog['init_net'].dev_name_head

for i in range(128):
    for dev in hlist_for_each_entry('struct net_device', dev_name_head, 'name_hlist'):
        name = dev.name.string_().decode()
        print(name)
    dev_name_head = dev_name_head + 1
