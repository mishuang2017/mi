#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import container_of
from drgn import Object

import sys
import os

sys.path.append(".")
from lib import *

act_base = prog['act_base']
print(act_base)
for tc_action_ops in list_for_each_entry('struct tc_action_ops', act_base.address_of_(), 'head'):
    print(tc_action_ops)
