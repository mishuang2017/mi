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
udpif = backer.udpif

ukeys = udpif.ukeys
# print(ukeys)

N_UMAPS = 512

for i in range(N_UMAPS):
    cmap = ukeys[i].cmap
    if cmap.impl.p.value_() != prog['empty_cmap'].address_of_().value_():
#         print(i)
        keys = print_cmap(cmap, "udpif_key", "cmap_node")
        for j, key in enumerate(keys):
#             print(key)
#             print_ufid(key.ufid)
            print("reval_seq: %d" % key.reval_seq)
            print(key.actions)
#             print("key_recird_id: %d" % key.key_recirc_id)
#             print(key.recircs)
            print('')

# print(prog['empty_cmap'].address_of_())
