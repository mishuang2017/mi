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

dev_list = prog['dev_list']

for dev in list_for_each_entry('struct cma_device', dev_list.address_of_(), 'list'):
    print(dev.device.dev.kobj.name)

exit(0)

devs = get_netdevs()
# print(devs)

jiffies = prog['jiffies']
print(jiffies)


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
# print(mdev.mlx5e_res)

num_bfregs = mdev.mlx5e_res.hw_objs.num_bfregs
print(num_bfregs)
for i in range(num_bfregs):
    print('-----------------------%d------------------------------' % i)
    print(mdev.mlx5e_res.hw_objs.bfregs[i])

def print_mlx5_uars_page(mdev):
    bfregs = mdev.priv.bfregs
    # print(bfregs)
    print('-----------------------reg_head------------------------------')
    for bfreg in list_for_each_entry('struct mlx5_uars_page', bfregs.reg_head.list.address_of_(), 'list'):
        print(bfreg)
    print('-----------------------wc_head------------------------------')
    for bfreg in list_for_each_entry('struct mlx5_uars_page', bfregs.wc_head.list.address_of_(), 'list'):
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
