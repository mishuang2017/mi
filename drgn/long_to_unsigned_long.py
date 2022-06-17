#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append(".")
from lib import *

mlx5_intf_mutex = prog['mlx5_intf_mutex']
print(mlx5_intf_mutex)

counter = mlx5_intf_mutex.owner.counter
print("%x" % (counter & 0xffffffffffffffff))
