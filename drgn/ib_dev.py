#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
from drgn import cast
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

mlx5_ib_dev = lib.get_mlx5_ib_dev()
if mlx5_ib_dev.address_of_().value_() == 0:
    sys.exit(0)

print("mlx5_ib_dev %lx" % mlx5_ib_dev.address_of_())
print("num_ports %d" % mlx5_ib_dev.num_ports)

ib_device = mlx5_ib_dev.ib_dev
print("phys_port_cnt: %d" % ib_device.phys_port_cnt)

port_list = ib_device.port_list
print(port_list)

i=0
# for port in list_for_each_entry('struct ib_port', port_list.address_of_(), 'kobj.entry'):
#     print(port.port_num.value_())


