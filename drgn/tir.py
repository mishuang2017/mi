#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

mlx5e_priv = lib.get_mlx5_pf0()
tirs_list = mlx5e_priv.mdev.mlx5e_res.td.tirs_list

i=1
for tir in list_for_each_entry('struct mlx5e_tir', tirs_list.address_of_(), 'list'):
    print("%4d: %x" % (i, tir.tirn))
    i=i+1
