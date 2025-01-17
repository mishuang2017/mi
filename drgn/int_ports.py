#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

sys.path.append(".")
from lib import *

print(sys.path)

mlx5e_priv = get_mlx5_pf0()
mlx5_eswitch = mlx5e_priv.mdev.priv.eswitch
ppriv = mlx5e_priv.ppriv
mlx5e_rep_priv = Object(prog, 'struct mlx5e_rep_priv', address=ppriv.value_())
uplink_priv = mlx5e_rep_priv.uplink_priv
print(uplink_priv.int_port_priv)
for port in list_for_each_entry('struct mlx5e_tc_int_port', uplink_priv.int_port_priv.int_ports.address_of_(), 'list'):
#     print(port)
    print("netdev index: %d" % port.ifindex)
    print(port.type)
    print("match_metadata: %x" % port.match_metadata)
    print_mlx5_flow_handle(port.rx_rule)
