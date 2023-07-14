#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

net = prog['init_net']
# print(net.proc_net)

rb_root = net.proc_net.subdir.address_of_()
print("rb_root %x" % rb_root)

for node in rbtree_inorder_for_each_entry("struct proc_dir_entry", rb_root, "subdir_node"):
    name = node.name.string_().decode()
    if name == "tcp":
        print(node)
