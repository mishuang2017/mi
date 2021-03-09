#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

net_namespace_list = prog['net_namespace_list']
for net in list_for_each_entry('struct net', net_namespace_list.address_of_(), 'list'):
    dev_base_head = net.dev_base_head.address_of_()

    print("\nstruct net %lx" % net.value_())
    for dev in list_for_each_entry('struct net_device', dev_base_head, 'dev_list'):
        name = dev.name.string_().decode()
        print(name)
