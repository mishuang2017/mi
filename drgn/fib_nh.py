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

fib_info_devhash = prog['fib_info_devhash']
size = 128

# enum {
#         RTN_UNSPEC,
#         RTN_UNICAST,            /* Gateway or direct route      */
#         RTN_LOCAL,              /* Accept locally               */
#         RTN_BROADCAST,          /* Accept locally as broadcast,
# 
# enum rt_scope_t {
#         RT_SCOPE_UNIVERSE=0,
# /* User defined values  */
#         RT_SCOPE_SITE=200,
#         RT_SCOPE_LINK=253,
#         RT_SCOPE_HOST=254,
#         RT_SCOPE_NOWHERE=255
# };
# 
# name:         br  saddr:    192.168.1.13  gw:         0.0.0.0  weight:    1  scope:  254  flags:    0  fib_info ffff9776a1a58f00  fib_type 1
# name:         br  saddr:    192.168.1.13  gw:         0.0.0.0  weight:    1  scope:  254  flags:    0  fib_info ffff9776a1a58e00  fib_type 3
# name:         br  saddr:    192.168.1.13  gw:         0.0.0.0  weight:    1  scope:  255  flags:    0  fib_info ffff9776a1a58b00  fib_type 2
 
broadcast = prog['RTN_BROADCAST']

def print_info(info):
    print("fib_nh %lx" % info.fib_nh[0].address_of_())
    print('')

def print_nh(nh):
    fib_info = nh.nh_parent
    name = nh.nh_dev.name.string_().decode()
    fib_type = nh.nh_parent.fib_type.value_()
    fib_scope = nh.nh_scope.value_()

#     if fib_scope == prog['RT_SCOPE_NOWHERE'].value_():
#         return
#     if fib_type == broadcast.value_():
#         return
#     if name != "br" and name != "enp4s0f0":
#         return

#     print("fib_nh %lx" % nh)
    print("name: %10s" % name, end='')
    print("  saddr: %15s" % lib.ipv4(socket.ntohl(nh.nh_saddr.value_())), end='')
    print("  gw: %15s" % lib.ipv4(socket.ntohl(nh.nh_gw.value_())), end='')
    print("  weight: %4d" % nh.nh_weight.value_(), end='')
    print("  scope: %4d" % nh.nh_scope.value_(), end='')
    print("  flags: %4x" % nh.nh_flags.value_(), end='')
    print("  fib_info %lx" % nh.nh_parent.value_(), end='')
    print("  fib_type %x" % nh.nh_parent.fib_type, end='')
    print('')
#     print_info(fib_info)

for i in range(size):
	for nh in hlist_for_each_entry('struct fib_nh', fib_info_devhash[i].address_of_(), 'nh_hash'):
            print_nh(nh)
