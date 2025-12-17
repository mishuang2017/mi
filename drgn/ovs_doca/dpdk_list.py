#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
from socket import ntohl
import socket

import subprocess
import drgn
import sys
import time

sys.path.append(".")
from lib_ovs import *

dpdk_list = prog['dpdk_list']
print(dpdk_list)

for netdev_doca in list_for_each_entry('struct netdev_doca', dpdk_list.address_of_(), 'list_node'):
    print(netdev_doca.tx_q)

ovs_doca_log = prog['ovs_doca_log']
print(ovs_doca_log)

log_stream= prog['ovs_doca_log']
print(log_stream)
