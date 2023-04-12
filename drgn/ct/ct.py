#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

sys.path.append("..")

from lib import *

size = prog['nf_conntrack_htable_size']
hash = prog['nf_conntrack_hash']
print("nf_conntrack_htable_size: %d" % size)

for i in range(size):
    head = hash[i]
#     print(head)
    if head.first.value_() & 0x1:
        continue;
    for tuple in hlist_nulls_for_each_entry("struct nf_conntrack_tuple_hash", head.address_of_(), "hnnode"):
        ct = container_of(tuple, "struct nf_conn", "tuplehash")
#         print("nf_conn %lx" % ct.value_())
#         print("nf_conntrack_tuple %lx" % tuple.value_())
#         print("")
        print_tuple(tuple, ct)
