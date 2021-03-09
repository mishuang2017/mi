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

fib_info_hash = prog['fib_info_hash']
size = prog['fib_info_hash_size']

for i in range(size):
    for fib in hlist_for_each_entry('struct fib_info', fib_info_hash[i].address_of_(), 'fib_hash'):
        print(fib)
