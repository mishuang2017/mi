#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append("..")
from lib import *

devices = prog['devices']
# print(devices)

#
# In file drivers/infiniband/core/device.c
# static DEFINE_XARRAY_FLAGS(devices, XA_FLAGS_ALLOC);
#

for node in radix_tree_for_each(devices.address_of_()):
    ib_device = Object(prog, 'struct ib_device', address=node[1].value_())
    print("\n=======================")
    print("ib_device.name %s" % ib_device.name.string_().decode())
    print("ib_device.dev.kobj.name %s" % ib_device.dev.kobj.name.string_().decode())
#     print(ib_device.phys_port_cnt)
