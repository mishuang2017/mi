#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

def print_stats(priv):
    mlx5_fc_stats = priv.mdev.priv.fc_stats

    counters_idr = mlx5_fc_stats.counters_idr

    print('=== idr ===')
    for node in radix_tree_for_each(counters_idr.idr_rt.address_of_()):
        fc = Object(prog, 'struct mlx5_fc', address=node[1].value_())
    #     print(fc)
        print("id: %x, packets: %d" % (fc.id, fc.cache.packets))

# print('=== list ===')
# for fc in list_for_each_entry('struct mlx5_fc',mlx5_fc_stats.counters.address_of_(), 'list'):
#     print("id: %x, packets: %d" % (fc.id, fc.cache.packets))

mlx5e_priv = get_mlx5_pf0()
print_stats(mlx5e_priv)
mlx5e_priv = get_mlx5_pf1()
print_stats(mlx5e_priv)
