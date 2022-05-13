#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

devs = get_netdevs()
# print(devs)

new_devs = [dev for dev in devs if dev.name.string_().decode().startswith("enp")]
# print(new_devs[0])


if new_devs[0] in new_devs:
    print("true")
else:
    print("false")

