#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append('.')

pernet_list = prog['pernet_list']

# i=1
# for pernet in list_for_each_entry('struct pernet_operations', pernet_list.address_of_(), 'list'):
#     print(i)
#     print(pernet)
#     i=i+1

netdev_chain = prog['netdev_chain']

i=1
head = netdev_chain.head
while head.next:
    print(i)
    print(head)
    head = head.next
    i=i+1

# i=1
# for pernet in list_for_each_entry('struct raw_notifier_head', pernet_list.address_of_(), 'list'):
#     print(i)
#     print(pernet)
 
