#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

root_fs = prog['root_fs']
print(root_fs)

# for i in range(root_fs.ar_size):
#     print(root_fs.children[i])

kernel_root_fs = (root_fs.children[4])
print(kernel_root_fs)

kernel_root_fs_ns = kernel_root_fs.children[0]

print(kernel_root_fs_ns)

for i in range(kernel_root_fs_ns.ar_size):
    print(kernel_root_fs_ns.children[i])
