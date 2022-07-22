#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5e_priv(pf0_name)
devcom = mlx5e_priv.mdev.priv.devcom
print(devcom.priv)

mlx5e_priv = get_mlx5e_priv(pf1_name)
# devcom = mlx5e_priv.mdev.priv.devcom
# print(devcom.priv)
