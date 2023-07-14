#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

list = prog['psample_groups_list']

for group in list_for_each_entry("struct psample_group", list.address_of_(), "list"):
    print(group)
