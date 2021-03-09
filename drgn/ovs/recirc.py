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

cmap = prog['id_map']
# print(cmap)
ids = print_cmap(cmap, "recirc_id_node", "id_node")

for i, id in enumerate(ids):
#     print(id)
    print("id: %d, table_id: %d, conntracked: %d," % (id.id, id.state.table_id, id.state.conntracked), end=' ')
    print("regs[3]: %10x, in_port: %d" % (id.state.metadata.regs[3], id.state.metadata.in_port))
