#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

devices = prog['devices']

for node in radix_tree_for_each(devices):
    ib_device = Object(prog, 'struct ib_device', address=node[1].value_())
    print("index: %x" % ib_device.index)

rdma_dev_net_id = prog['rdma_dev_net_id']
print("rdma_dev_net_id: %x " % rdma_dev_net_id)
