#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

print(sys.path)

devs = get_netdevs()
# print(devs)

new_devs = [dev for dev in devs if dev.name.string_().decode().startswith("enp")]
# print(new_devs[0])


if new_devs[0] in new_devs:
    print("true")
else:
    print("false")


print(__name__)

mlx5e_priv = get_mlx5_pf0()
print(mlx5e_priv.wq)
