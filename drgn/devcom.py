#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

print(" ===== port 1 =====")

mlx5e_priv = get_mlx5e_priv(pf0_name)
devcom = mlx5e_priv.mdev.priv.devcom
print(devcom.idx)
print(devcom.priv)
# print(devcom.priv.components[0].device)
esw = Object(prog, 'struct mlx5_eswitch *', address=devcom.priv.components[0].device[0].data)
print("%x" % esw.dev.address_of_())
esw = Object(prog, 'struct mlx5_eswitch *', address=devcom.priv.components[0].device[1].data)
print("%x" % esw.dev.address_of_())
print(devcom.priv.devs)

print(" ===== port 2 =====")

mlx5e_priv = get_mlx5e_priv(pf1_name)
devcom = mlx5e_priv.mdev.priv.devcom
print(devcom.idx)
print(devcom.priv)

print(" ==== devcom_list ==== ")
devcom_list = prog['devcom_list']
for devcom in list_for_each_entry('struct mlx5_devcom_list', devcom_list.address_of_(), 'list'):
    print(devcom)
