#!/usr/local/bin/drgn -k

from drgn import container_of
from drgn.helpers.linux import *
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

table_addr = lib.name_to_address("_flowtable")
print("%lx" % table_addr)

try:
    t = prog['_flowtable0']
except LookupError as x:
    print("LookupError")
    sys.exit(1)
