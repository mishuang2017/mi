#!/usr/local/bin/drgn -k

# macvlan_common_newlink
#     netdev_upper_dev_link
#         __netdev_upper_dev_link

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

sys.path.append(".")
from lib import *

mlx5e_priv = get_mlx5_pf0()
netdev = mlx5e_priv.netdev
print(netdev.name)
print(netdev.adj_list.upper)
for netdev_adjacent in list_for_each_entry('struct netdev_adjacent', netdev.adj_list.upper.address_of_(), 'list'):
    macvlan_netdev = netdev_adjacent.dev
    print(macvlan_netdev.name)
    macvlan_dev_addr = macvlan_netdev.value_() + prog.type('struct net_device').size
    macvlan_dev = Object(prog, 'struct macvlan_dev', address=macvlan_dev_addr)
    print(macvlan_dev)
#     print(macvlan_dev.port)
