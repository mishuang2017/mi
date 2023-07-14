#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
from socket import ntohl
import socket

import subprocess
import drgn
import sys
import time

sys.path.append(".")
from lib_ovs import *

ofproto_dpif = get_ofproto_dpif("br")

print("ofproto_dpif: %lx" % ofproto_dpif)

ml = ofproto_dpif.ml
print(ml)

lrus = ml.lrus

for e in list_for_each_entry('struct mac_entry', lrus.address_of_(), 'lru_node'):
    print(e)
    mlport = e.mlport
    print(mlport)

    ofbundle = Object(prog, 'struct ofbundle', address=mlport.port)
    print(ofbundle)
