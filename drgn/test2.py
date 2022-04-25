#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append(".")
from lib import *

mlx5_core_devs = get_mlx5_core_devs()
print(mlx5_core_devs)

print('')
for k, v in mlx5_core_devs.items():
    print(k)
    print("mlx5_core_dev %x" % v.address_of_())
    print("mlx5_eswtich  %x" % v.priv.eswitch.address_of_())
    print(v.priv.eswitch)
