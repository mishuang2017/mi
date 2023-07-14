#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

sys.path.append(".")
from lib import *

debug_locks = prog['debug_locks']
print("debug_locks: %d" % debug_locks)

lock_classes = prog['lock_classes']

# for i in range(100):
#     print(lock_classes[i].name.string_().decode())

i=0
all_lock_classes = prog['all_lock_classes']
for lock in list_for_each_entry('struct lock_class', all_lock_classes.address_of_(), 'lock_entry'):
    i=i+1
#     print(i)
#     print(lock.key)

print("number of all_lock_classes: %d" % i)

nr_lock_classes = prog['nr_lock_classes']
print("nr_lock_classes: %d" % nr_lock_classes)

# nr_zapped_classes = prog['nr_zapped_classes']
# print("nr_zapped_classes: %d" % nr_zapped_classes)
