#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
from lib import *

# net_namespace_list = prog['net_namespace_list']
# for net in list_for_each_entry('struct net', net_namespace_list.address_of_(), 'list'):
#     dev_base_head = net.dev_base_head.address_of_()

NFPROTO_NUMPROTO = prog['NFPROTO_NUMPROTO']

gen = prog['init_net'].gen
id = prog['xt_pernet_id']
print("xt_pernet_id: %d" % id)
ptr = gen.ptr[id]
xt_pernet = Object(prog, 'struct xt_pernet', address=ptr.value_())
# print(xt_pernet)

for i in range(NFPROTO_NUMPROTO):
    print(i)
    for table in list_for_each_entry('struct xt_table', xt_pernet.tables[i].address_of_(), 'list'):
        print(table)
        print(table.private)
