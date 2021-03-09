#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import socket
import sys
import os

sys.path.append("..")
from lib import *

for node in radix_tree_for_each(prog['genl_fam_idr'].idr_rt):
    genl = Object(prog, 'struct genl_family', address=node[1].value_())
    if genl.name.string_().decode() == "psample":
        print(genl)
    if genl.name.string_().decode() == "nlctrl":
        print(genl)
