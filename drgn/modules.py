#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append('.')
from lib import *

modules = prog['modules']

for module in list_for_each_entry("struct module", modules.address_of_(), 'list'):
    name = module.name.string_().decode()
    if name != "bonding" and name != "mlx5_ib" and name != "mlx5_core":
        continue
    print("%10s" % name, end='\t')
    print(module.refcnt.counter.value_())
