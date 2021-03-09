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

cmap = prog['netdev_flow_apis']
# print(cmap)
ids = print_cmap(cmap, "netdev_registered_flow_api", "cmap_node")

for i, id in enumerate(ids):
    print(id)

netdev_offload_tc = prog['netdev_offload_tc']
print(netdev_offload_tc)
