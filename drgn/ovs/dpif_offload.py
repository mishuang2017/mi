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

shashes = print_hmap(prog['dpif_classes'].map, "shash_node", "node")

print("\n=== dpif_classes ===\n")
for i, shash in enumerate(shashes):
    dpif = Object(prog, 'struct registered_dpif_class', address=shash.data)
    print(dpif)
    print(dpif.dpif_class.type)

print("\n=== dpif_offload_classes ===")
shashes = print_hmap(prog['dpif_offload_classes'].map, "shash_node", "node")
for i, shash in enumerate(shashes):
    print("\n\t=== %d ===\n" % i)
    dpif_offload = Object(prog, 'struct registered_dpif_offload_class', address=shash.data)
    print(dpif_offload)
    print(dpif_offload.offload_class)
