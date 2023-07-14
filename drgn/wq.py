#!/usr/local/bin/drgn -k

from drgn import container_of
from drgn.helpers.linux import *
from drgn import Object

import sys
import os

sys.path.append(".")
import lib

wqs =  prog['workqueues'].address_of_()
# print(wqs)
for wq in list_for_each_entry('struct workqueue_struct', wqs, 'list'):
    name = wq.name.string_().decode()
#     print(name)
    if name == "mlx5e":
        break

print(wq)
