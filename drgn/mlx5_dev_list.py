#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object
import time
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

mlx5_dev_list = prog['mlx5_dev_list']
for priv in list_for_each_entry('struct mlx5_priv', mlx5_dev_list.address_of_(), 'dev_list'):
    dev = container_of(priv, "struct mlx5_core_dev", "priv")
    print(dev.device.kobj.name)
