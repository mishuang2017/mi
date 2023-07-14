#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

veths = lib.get_veth("host1_rep")
devs = lib.get_veth_netdev("host1_rep")
print(devs[0].vstats)
