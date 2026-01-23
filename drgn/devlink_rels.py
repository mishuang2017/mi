#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

devlink_rels = prog['devlink_rels']
for node in radix_tree_for_each(devlink_rels.address_of_()):
    print('-------------------------------------')
    rel = Object(prog, 'struct devlink_rel', address=node[1].value_())
    print("rel.index: %d, rel.devlink_index: %d, nested_in.devlink_index: %d" % (rel.index, rel.devlink_index, rel.nested_in.devlink_index))
#     print(rel)
