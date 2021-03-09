#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

inet_addr_list = prog['inet_addr_lst']
size = 128

for i in range(size):
    for ip in hlist_for_each_entry('struct in_ifaddr', inet_addr_list[i].address_of_(), 'hash'):
        print("ifa_address: %15s, ifa_label: %10s, ifa_dev.dev: %lx" % \
            (lib.ipv4(socket.ntohl(ip.ifa_address.value_())), ip.ifa_label.string_().decode(), ip.ifa_dev.dev))
