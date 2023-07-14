#!/usr/local/bin/drgn -k

# type:  800, func:     ip_rcv, list_func:     ip_list_rcv, id_match: 0x0
# type:   11, func:    llc_rcv, list_func:             0x0, id_match: 0x0
# type:    4, func:    llc_rcv, list_func:             0x0, id_match: 0x0
# type:  806, func:    arp_rcv, list_func:             0x0, id_match: 0x0
# type: 86dd, func:   ipv6_rcv, list_func:   ipv6_list_rcv, id_match: 0x0

from drgn.helpers.linux import *
from drgn import Object
import time
import socket
import sys
import os

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

def print_packet_type(pt):
    type = pt.type.value_()
    func = pt.func.value_()
    list_func = pt.list_func.value_()
    id_match = pt.id_match.value_()
    print("type: %4x, func: %10s, list_func: %15s, id_match: %s" % \
        (socket.ntohs(type),                    \
        lib.address_to_name(hex(func)),        \
        lib.address_to_name(hex(list_func)),        \
        lib.address_to_name(hex(id_match))))
#     print(pt)

for i in range(16):
    ptype_base = prog['ptype_base']
    for pt in list_for_each_entry('struct packet_type', ptype_base[i].address_of_(), 'list'):
        print_packet_type(pt)
