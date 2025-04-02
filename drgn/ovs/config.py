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

print("block_support: %d" % prog['block_support'])
print("enc_flags_support: %d" % prog['enc_flags_support'])

print("monitor_running: %d" % prog['monitor_running'])
print("monitor_tid: %d" % prog['monitor_running'])
print("n_revalidators: %d" % prog['n_revalidators'])
print("n_handlers: %d" % prog['n_handlers'])

print('')
print("ovs_datapath_family:         %2d, used for revalidator,      kernel function ovs_dp_cmd_new" % prog['ovs_datapath_family'])
print("ovs_vport_family:            %2d" % prog['ovs_vport_family'])
print("ovs_flow_family:             %2d, used for install dp flows, kernel function ovs_flow_cmd_new" % prog['ovs_flow_family'])
print("ovs_packet_family:           %2d, used for receive upcall and execute commands, userspace function dpif_netlink_encode_execute, kernel function queue_userspace_packet" % prog['ovs_packet_family'])
print("ovs_vport_mcgroup:           %2d" % prog['ovs_vport_mcgroup'])
print("ovs_meter_family:            %2d" % prog['ovs_meter_family'])
print("ovs_ct_limit_family:         %2d" % prog['ovs_ct_limit_family'])

# print("psample_family:              %2d" % prog['psample_family'])
# print("psample_mcgroup:             %2d" % prog['psample_mcgroup'])

print("next_id:                     %2d" % prog['next_id'])
print("netdev_flow_api_enabled:     %2d" % prog['netdev_flow_api_enabled'])

print("n_coverage_counters:         %2d" % prog['n_coverage_counters'])
print("allocated_coverage_counters: %2d" % prog['allocated_coverage_counters'])

# psample_sock = prog['psample_sock']
# print(psample_sock)

# n_coverage_counters = prog['n_coverage_counters']
# coverage_counters = prog['coverage_counters']
# for i in range(n_coverage_counters):
#     print(coverage_counters[i])
#     total = coverage_counters[i].total
#     last_total = coverage_counters[i].last_total
#     name = coverage_counters[i].name
#     if total:
#         print("%80s, %5d, %5d" % (name, total, last_total))

# sample_group_ids = prog['sample_group_ids']
# print(sample_group_ids)
