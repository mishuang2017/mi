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

for node in radix_tree_for_each(devices.address_of_()):
    ib_device = Object(prog, 'struct ib_device', address=node[1].value_())
    print(ib_device.name)
