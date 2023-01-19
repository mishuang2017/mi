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

meter_police_ids = prog['meter_police_ids']
print(meter_police_ids)
meters = print_hmap(meter_police_ids.map.address_of_(), "id_node", "node")
for i, id in enumerate(meters):
    print(id)
