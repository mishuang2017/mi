#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
from drgn import cast
import time
import socket
import sys
import os

sys.path.append("..")
from lib import *

indr_setup_block_ht = prog['indr_setup_block_ht']
# print(indr_setup_block_ht)

def print_indr_setup_block_ht(block):
    print(block)
    print(block.dev.name.string_().decode())
    cb_list = block.cb_list
#     print(cb_list)
    for e in list_for_each_entry('struct flow_indr_block_cb', cb_list.address_of_(), 'list'):
        print(e)
        print(address_to_name(hex(e.cb)))
        priv = Object(prog, "struct mlx5e_rep_priv", address=e.cb_priv.address_of_())
#         print(priv)
        print("mlx5e_rep_priv %lx" % e.cb_priv.address_of_())

for i, block in enumerate(hash(indr_setup_block_ht, 'struct flow_indr_block_dev', 'ht_node')):
    print("\n====== %d ========" % i)
    print_indr_setup_block_ht(block)
