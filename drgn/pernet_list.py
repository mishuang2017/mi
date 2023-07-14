#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append('.')

# pernet_list = prog['pernet_list']
# i=1
# for pernet in list_for_each_entry('struct pernet_operations', pernet_list.address_of_(), 'list'):
#     print(i)
#     print(pernet)
#     i=i+1

def print_netdev_chain(chain):
    i=1
    head = chain.head
    while head.next:
        print(i)
        print(head)
        head = head.next
        i=i+1

# eg. mlx5_netdev_event
# netdev_chain = prog['netdev_chain']
# print_netdev_chain(netdev_chain)

# eg. mlx5_esw_bridge_switchdev_port_event
init_net_netdev_chain = prog['init_net'].netdev_chain
print_netdev_chain(init_net_netdev_chain)
