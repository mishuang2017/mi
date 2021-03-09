#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import sys
import os
import time

libpath = os.path.dirname(os.path.realpath("__file__"))
sys.path.append(libpath)
import lib

while 1:
    rtnl = prog['rtnl_mutex']
    addr = rtnl.owner.counter

    if addr == 0:
        print("no owner")
        time.sleep(1)
        continue

    addr = addr & 0xfffffffffffffffe
    task = Object(prog, 'struct task_struct', address=addr)
    print(task.comm.string_().decode())
    time.sleep(1)
