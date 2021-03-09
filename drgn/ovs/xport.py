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

xbridge = get_xbridge("br")
xports = xbridge.xports
print(xports)

ports = print_hmap(xports, "xport", "ofp_node")

for i, port in enumerate(ports):
    print(port)
