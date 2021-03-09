#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5_pf0()
esw = mlx5e_priv.mdev.priv.eswitch
# print(esw.manager_vport)
print(mlx5e_priv.fs.ttc.ft.t)

priv2 = get_mlx5_pf1()
esw2 = priv2.mdev.priv.eswitch
