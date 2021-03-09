#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

net_todo_list = prog['net_todo_list']
print(net_todo_list)
for dev in list_for_each_entry('struct net_device', net_todo_list, 'todo_list'):
    print(dev.name)
