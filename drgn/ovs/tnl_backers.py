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
tnl_backers = backer.tnl_backers

print(tnl_backers)
print(tnl_backers.map.buckets)

simaps = print_hmap(tnl_backers.map, "simap_node", "node")
for i, simap in enumerate(simaps):
    print(simap)
