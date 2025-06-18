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
    print(priv.channels)
    num = priv.channels.num.value_()
    print("num of channels: %d" % num)
    channels = priv.channels.c

    for i in range(num):
#     for i in range(1):
        print("channel[%d]" % i, end=' ')
#         print(channels[i])
#         print(channels[i].sq[0].cq.mcq.irqn.value_())
        print("sqn: %#x" % channels[i].sq[0].sqn)
#         print(channels[i].rq.stats)
        print("rq.cq.mcq.irqn: %d" % channels[i].rq.cq.mcq.irqn.value_())

#         print(channels[i].sq[0].cq.mcq.vector.value_())
#         print(channels[i].rq.cq.mcq.vector.value_())

#         print(channels[i].sq[0].cq.mcq.tasklet_ctx.comp)
#         print(channels[i].rq.cq.mcq.tasklet_ctx.comp)

        print(channels[i].sq[0].cq)
        print("sq[0].cq.napi: %d" % channels[i].sq[0].cq.napi.napi_id.value_())
        print("rq.cq.napi: %d" % channels[i].rq.cq.napi.napi_id.value_())


priv = get_mlx5e_priv(pf0_name)
print(priv.channels.params.rx_cq_moderation)
print(priv.channels.params.tx_cq_moderation)
# print(priv.channels.params)

# print_channel(priv)
