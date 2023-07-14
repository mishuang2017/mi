#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)

from lib import *

size = prog['nf_nat_htable_size']
hash = prog['nf_nat_bysource']
print("nf_nat_htable_size: %d" % size)

IP_CT_DIR_ORIGINAL = prog['IP_CT_DIR_ORIGINAL'].value_()

for i in range(size):
    head = hash[i]
    for ct in hlist_for_each_entry("struct nf_conn", head.address_of_(), "nat_bysource"):
        tuple = ct.tuplehash[IP_CT_DIR_ORIGINAL]
        print_tuple(tuple, ct)
