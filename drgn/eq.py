#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
# import lib
from lib import *

mlx5e_priv =  get_mlx5e_priv("ens1f0")
eq_table = dev = mlx5e_priv.mdev.priv.eq_table

num = eq_table.num_comp_eqs.value_()
print("num_comp_eqs: %d" % num)

for comp in list_for_each_entry('struct mlx5_eq_comp', eq_table.comp_eqs_list.address_of_(), "list"):
    print("eqn: %d" % comp.core.eqn.value_())
    radix_tree_root = comp.core.cq_table.tree
    n = 1;
    for i in radix_tree_for_each(radix_tree_root):
        mlx5_core_cq = Object(prog, 'struct mlx5_core_cq', address=i[1])
        print("%d: cqn: %d " % (n, mlx5_core_cq.cqn.value_()), end="")
        print(mlx5_core_cq.tasklet_ctx)
        if n == 1:
            break;
        n = n + 1
    print("")
