#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
import socket

import subprocess
import drgn
import sys
import time

sys.path.append(".")
from lib_ovs import *

ovsrec_open_vswitch_columns = prog['ovsrec_open_vswitch_columns']

OVSREC_OPEN_VSWITCH_COL_BRIDGES = prog['OVSREC_OPEN_VSWITCH_COL_BRIDGES'].value_()
print(OVSREC_OPEN_VSWITCH_COL_BRIDGES)
# print(ovsrec_open_vswitch_columns[OVSREC_OPEN_VSWITCH_COL_BRIDGES])

OVSREC_OPEN_VSWITCH_COL_OTHER_CONFIG = prog['OVSREC_OPEN_VSWITCH_COL_OTHER_CONFIG'].value_()
print(OVSREC_OPEN_VSWITCH_COL_OTHER_CONFIG)

print(dir(ovsrec_open_vswitch_columns))
# print(help(ovsrec_open_vswitch_columns))
# print(ovsrec_open_vswitch_columns.type_())

ovsrec_table_classes = prog['ovsrec_table_classes']
OVSREC_TABLE_OPEN_VSWITCH = prog['OVSREC_TABLE_OPEN_VSWITCH'].value_()
print(ovsrec_table_classes[OVSREC_TABLE_OPEN_VSWITCH].columns[11])
