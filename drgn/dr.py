#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object
from drgn import cast
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

dev = lib.get_mlx5_core_dev(0)
print(dev.coredev_type)
# print(dev.dm)

priv = dev.priv
steering = priv.steering
print("esw->dev->priv.steering->mode: ", end='')
print(steering.mode)

root_ns = steering.fdb_root_ns.ns
mlx5_flow_root_namespace = Object(prog, 'struct mlx5_flow_root_namespace', address=root_ns.address_of_())
# print(root_ns)
# print(mlx5_flow_root_namespace)
fs_dr_domain = mlx5_flow_root_namespace.fs_dr_domain
print(fs_dr_domain.dr_domain.refcount)
print(fs_dr_domain.dr_domain)
