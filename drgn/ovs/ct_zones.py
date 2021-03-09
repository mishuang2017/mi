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

backer = get_backer()

cmap = backer.ct_zones
# print(cmap)
ct_zones = print_cmap(cmap, "ct_zone", "node")

for i, ct_zone in enumerate(ct_zones):
    print(ct_zone)

# for i in ('netdev_linux_class', 'netdev_internal_class'):
#     new_class = prog[i]
#     print("%10s, netdev_class: %lx" % (new_class.type, new_class.address_of_().value_()))
