#!/usr/local/bin/drgn -k

from drgn import container_of
from drgn.helpers.linux import *
from drgn import Object

import sys
import os
import string

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

try:
    buf = prog['__mlx5_log_buf']
except LookupError as x:
    print("no mlx5_buf")
    sys.exit(1)

result = {}

# print(buf.string_().decode("utf-8"))
for line in buf.string_().decode("utf-8").split('\n'):
#     print(line)
    index = line.split(':')[0]
    if len(index) != 0 and index.strip().isdigit():
        index = int(index)
#         print(index)
        result[index] = line

L=list(result.items()) 
L.sort()

for i in L:
    print(i[1])
