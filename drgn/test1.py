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

jiffies = prog['jiffies']
print(jiffies)

# exit(0)

IP_CT_ESTABLISHED_REPLY = prog['IP_CT_ESTABLISHED_REPLY']
print("%d" % IP_CT_ESTABLISHED_REPLY)

new_devs = [dev for dev in devs if dev.name.string_().decode().startswith("enp")]
# print(new_devs[0])


if new_devs[0] in new_devs:
    print("true")
else:
    print("false")

mlx5e_priv = get_mlx5_pf0()
print(mlx5e_priv.netdev.name)
mlx5e_priv = get_mlx5_pf1()
print(mlx5e_priv.netdev.name)

mdev = mlx5e_priv.mdev

bfregs = mdev.priv.bfregs
print(bfregs)
for bfreg in list_for_each_entry('struct mlx5_uars_page', bfregs.reg_head.list.address_of_(), 'list'):
    print(bfreg)


# https://drgn.readthedocs.io/en/latest/case_studies/kyber_stack_trace.html

# i=1
# for task in for_each_task(prog):
#     print("\n=================== %4d: %x ==================\n" % (i, task))
#     i=i+1
#     trace = prog.stack_trace(task)
#     print(trace)

# print(trace)
# dev = trace[17]["dev"]
# flow = trace[17]["flow"]
# print(dev.name)
# print(flow)

# task = per_cpu(prog["runqueues"], prog["crashing_cpu"]).curr
# print(task)
# print(prog.stack_trace(task))
