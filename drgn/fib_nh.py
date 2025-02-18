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

for i in range(size):
	for nh in hlist_for_each_entry('struct fib_nh', fib_info_devhash[i].address_of_(), 'nh_hash'):
            lib.print_fib_nh(nh)

for event in prog.type("enum rt_scope_t").enumerators[:-1]:
    print(event.name)
    print(event.value)

print(prog.type("enum rt_scope_t").enumerators[0])

RT_SCOPE_UNIVERSE = prog['RT_SCOPE_UNIVERSE']
print(RT_SCOPE_UNIVERSE)

RT_SCOPE_SITE = prog['RT_SCOPE_SITE']
print(RT_SCOPE_SITE)

if RT_SCOPE_SITE == prog.type("enum rt_scope_t").enumerators[1].value:
    print("yes")
