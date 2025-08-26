#!/usr/local/bin/drgn -k

from drgn.helpers.linux import *
from drgn import Object
import time
import sys
import os

sys.path.append("..")
from lib import *

devices = prog['devices']
# print(devices)

#
# In file drivers/infiniband/core/device.c
# static DEFINE_XARRAY_FLAGS(devices, XA_FLAGS_ALLOC);
#

for node in radix_tree_for_each(devices.address_of_()):
#     print(node)
    ib_device = Object(prog, 'struct ib_device', address=node[1].value_())
    print("ib_device %x" % node[1].value_())
    print("ib_device.dev.kobj.name %s" % ib_device.dma_device.kobj.name.string_().decode())
    print("ib_device.is_switch: %d" % ib_device.is_switch)
    print("ib_device.phys_port_cnt: %d" % ib_device.phys_port_cnt)
    print(ib_device.port_data[0].immutable)
#     print("   device name: %s" % ib_device.dev.kobj.name.string_().decode())
#     print(ib_device)
#     print("device.dev.kobj.name %s" % ib_device.dev.kobj.name.string_().decode())
#     print(ib_device.phys_port_cnt)
    print("\n=======================")

exit(0)

ib_mad_port_list = prog['ib_mad_port_list']

print('========================= ib_mad_port_list ===========================')
for ib_mad_port_private in list_for_each_entry('struct ib_mad_port_private', ib_mad_port_list.address_of_(), 'port_list'):
#     print(ib_mad_port_private.port_num)
    
    print("ib_device %x" % ib_mad_port_private.device)
    print("ib_device name: %s" % (ib_mad_port_private.device.dma_device.kobj.name.string_().decode()))
    print("   device name: %s" % ib_mad_port_private.device.dev.kobj.name.string_().decode())
    # print(ib_mad_port_private.qp_info[0].qp) # no SMI
    print("ib_mad_port_private.qp_info[1].qp.qp_num: %d" % ib_mad_port_private.qp_info[1].qp.qp_num)
    print(ib_mad_port_private.qp_info[1].qp.qp_type)
#     print(ib_mad_port_private.qp_info[1].qp)
    print("\n=======================")
    print(ib_mad_port_private.device);

ucma_cmd_table = prog['ucma_cmd_table']
print(ucma_cmd_table)

cm = prog['cm']
# print(cm)

for id in rbtree_inorder_for_each_entry("struct cm_id_private", cm.listen_service_table, "service_node"):
    print(id.qp_type)

for cm_dev in list_for_each_entry('struct cm_device', cm.device_list.address_of_(), 'list'):
    print(cm_dev.ib_device.dma_device.kobj.name.string_().decode())
#     print(cm_dev)
#     print(cm_dev.port[0])
#     print(cm_dev.port[0].mad_agent)
