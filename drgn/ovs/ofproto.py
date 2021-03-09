#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
from drgn import container_of
from socket import ntohl
import socket

import subprocess
import drgn
import sys
import time

sys.path.append(".")
from lib_ovs import *

ofproto_dpif = get_ofproto_dpif("br")

print("ofproto_dpif: %lx" % ofproto_dpif)

ofproto = ofproto_dpif.up
print("ofproto.type: %s" % ofproto.type)

print(ofproto_dpif.sflow)

# ofproto_dpif = container_of(ofproto.address_of_(), "struct ofproto_dpif", "up")
parts = ofproto_dpif.uuid.parts
print("%x-%x-%x-%x" % \
    (ntohl(parts[0].value_()),
     ntohl(parts[1].value_()),
     ntohl(parts[2].value_()),
     ntohl(parts[3].value_())))

tables_version = ofproto.tables_version
print("tables_version: %d" % tables_version)

set_sflow = ofproto.ofproto_class.set_sflow
print(address_to_name(hex(set_sflow.value_())))

set_tables_version = ofproto.ofproto_class.set_tables_version
print(address_to_name(hex(set_tables_version.value_())))

# print(ofproto.ofproto_class)

print("change_seq: %d" % ofproto.change_seq)

ofproto_ports = print_hmap(ofproto.ports.address_of_(), "ofport", "hmap_node")
for j, ofproto_port in enumerate(ofproto_ports):
    print("name: %15s, ofp_port: %d" % (ofproto_port.netdev.name.string_().decode(), ofproto_port.ofp_port))
#     print(ofproto_port)
#     print(ofproto_port.netdev)

# n_tables = ofproto.n_tables
# print(n_tables)
for i in range(2):
    table = ofproto.tables[i]
    cls = table.cls
    n_rules = cls.n_rules
    print("table[%d] has %d rules" % (i, n_rules))
