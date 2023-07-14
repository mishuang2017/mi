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

# prios = prog['prios']
# print(prios)

# last_prio = prog['last_prio']
xcfgp = prog['xcfgp']
print(xcfgp)

# ports = print_hmap(xports, "xport", "ofp_node")

# for i, port in enumerate(ports):
#     print(port)
