#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

psample_nl_family = prog['psample_nl_family']
print(psample_nl_family)

mcgrp_offset = psample_nl_family.mcgrp_offset.value_()
print("mcgrp_offset: %d" % mcgrp_offset)
