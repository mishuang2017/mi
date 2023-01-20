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
    print("id: %x" % id.id)

meter_id_to_police_idx = prog['meter_id_to_police_idx']
meters = print_hmap(meter_id_to_police_idx.address_of_(), "meter_police_mapping_data", "meter_id_node")
for i, meter in enumerate(meters):
    print(meter)
    print("meter id: %x, police id: %x" % (meter.meter_id, meter.police_idx))
