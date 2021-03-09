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

cmap = prog['netdev_classes']
classes = print_cmap(cmap, "netdev_registered_class", "cmap_node")

for i, new_class in enumerate(classes):
    print(new_class)

for i in ('netdev_linux_class', 'netdev_internal_class'):
    new_class = prog[i]
    print(new_class)
#     print("%10s, netdev_class: %lx" % (new_class.type, new_class.address_of_().value_()))
