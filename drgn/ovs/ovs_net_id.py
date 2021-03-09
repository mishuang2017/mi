#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

gen = prog['init_net'].gen
id = prog['ovs_net_id']
print("ovs_net_id: %d" % id)
ptr = gen.ptr[id]
ovs_net = Object(prog, 'struct ovs_net', address=ptr.value_())
print("ovs_net %lx" % ovs_net.address_of_())
print(ovs_net)

for dp in list_for_each_entry('struct datapath', ovs_net.dps.address_of_(), 'list_node'):
    print(dp)
