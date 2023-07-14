#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
# import lib
from lib import *

# priv = lib.get_mlx5e_priv("ens1f0")

def print_channel(priv):
    num = priv.channels.num.value_()
    print("num of channels: %d" % num)
    channels = priv.channels.c

    for i in range(num):
#     for i in range(1):
        print("channel[%d]" % i)
#         print(channels[i].sq[0].cq.mcq.irqn.value_())
        print("sqn: %x" % channels[i].sq[0].sqn)
#         print(channels[i].rq.cq.mcq.irqn.value_())

#         print(channels[i].sq[0].cq.mcq.vector.value_())
#         print(channels[i].rq.cq.mcq.vector.value_())

#         print(channels[i].sq[0].cq.mcq.tasklet_ctx.comp)
#         print(channels[i].rq.cq.mcq.tasklet_ctx.comp)

#         print("sq[0].cq.napi: %d" % channels[i].sq[0].cq.napi.napi_id.value_())
#         print("rq.cq.napi: %d" % channels[i].rq.cq.napi.napi_id.value_())


for x, dev in enumerate(get_netdevs()):
    name = dev.name.string_().decode()
    addr = dev.value_()
    if "enp" not in name:
        continue;
    print("\n===%s===" % name)

    mlx5e_priv_addr = addr + prog.type('struct net_device').size
    mlx5e_priv = Object(prog, 'struct mlx5e_priv', address=mlx5e_priv_addr)
    print_channel(mlx5e_priv)
