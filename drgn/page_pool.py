#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
# import lib
from lib import *

page_pools = prog['page_pools']
print(page_pools)
for node in radix_tree_for_each(page_pools.address_of_()):
    pool = Object(prog, 'struct page_pool', address=node[1].value_())
    print(pool.slow)
#     print(node)
