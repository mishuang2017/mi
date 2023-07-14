#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append(".")
import lib

gen = prog['init_net'].gen
id = prog['fib_notifier_net_id']
print("fib_notifier_net_id: %d" % id)
ptr = gen.ptr[id]
fib_notifier_net = Object(prog, 'struct fib_notifier_net', address=ptr.value_())
print("fib_notifier_net %lx" % fib_notifier_net.address_of_())
# print(fib_notifier_net)
fib_chain = fib_notifier_net.fib_chain
# print(fib_chain)
head = fib_chain.head

while head.value_():
    print(head)
    head = head.next
