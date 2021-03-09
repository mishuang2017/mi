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
odp_to_ofport_map = backer.odp_to_ofport_map

ofport_dpifs = print_hmap(odp_to_ofport_map, "ofport_dpif", "odp_port_node")
for i, ofport_dpif in enumerate(ofport_dpifs):
    print(ofport_dpif)
