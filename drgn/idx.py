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

# u16 mlx5e_log_next_seq = 0;
# u32 mlx5e_log_next_idx = 0;

try:
    seq = prog['mlx5e_log_next_seq']
    idx = prog['mlx5e_log_next_idx']
except LookupError as x:
    print("no mlx5_buf")
    sys.exit(1)

print("seq: %d" % seq.value_())
print("idx: %d" % idx.value_())
